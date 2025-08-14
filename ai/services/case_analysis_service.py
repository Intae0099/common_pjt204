from langchain.chains import LLMChain
from langchain.llms.base import LLM
from typing import List, Dict, Optional
import json
import re

from config.tags import SPECIALTY_TAGS
from config.settings import get_llm_settings
from llm.llm_response_parser import CotOutputParser, parse_case_analysis_output, CaseAnalysisResult
from llm.prompt_templates import get_cot_prompt
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel
from services.search_service import SearchService
from services.lawyer_recommendation_service import LawyerRecommendationService
from utils.logger import LoggerMixin
from utils.exceptions import handle_service_exceptions, LLMError
from utils.confidence_calculator import ConfidenceCalculator

class CaseAnalysisService(LoggerMixin):
    def __init__(self, llm: LLM, search_service: SearchService, lawyer_recommendation_service: Optional[LawyerRecommendationService] = None):
        """
        LLM 객체와 검색 서비스를 주입받아 초기화합니다.

        Args:
            llm (LLM): LangChain의 LLM 인터페이스를 구현한 객체
            search_service (SearchService): 검색 서비스 인스턴스
            lawyer_recommendation_service (LawyerRecommendationService, optional): 변호사 추천 서비스
        """
        self.llm = llm
        self.search_service = search_service
        self.lawyer_recommendation_service = lawyer_recommendation_service
        self.prompt_template = get_cot_prompt()
        self.parser = CotOutputParser()
        self.confidence_calculator = ConfidenceCalculator()  # 신뢰도 계산기 추가
        # `prompt | llm` 로 RunnableSequence를 만듭니다. (LangChain 0.1.17 이상 권장 방식)
        self.chain = self.prompt_template | self.llm

    @handle_service_exceptions("법률 분석 처리 중 오류가 발생했습니다.")
    async def analyze_case(
            self,
            user_query: str,
            top_k_docs: int = 5, # RAG를 위한 top_k 인자 추가
            recommend_lawyers: bool = True # 변호사 추천 옵션
        ) -> dict:
            """
            Args:
                user_query: 사용자가 물어본 질문
                top_k_docs: 검색할 관련 판례의 개수
                recommend_lawyers: 변호사 추천 포함 여부
            """
            self.logger.info(f"Starting case analysis for query: {user_query[:100]}...")
            # 1. 관련 판례 검색 (RAG)
            # Call vector_search method of SearchService
            retrieved_docs, _ = await self.search_service.vector_search(user_query, size=top_k_docs)

            # 2. 검색된 판례 청크를 LLM 입력 형식에 맞게 변환
            # 이제 search_service는 chunk_text를 포함하여 반환합니다.
            formatted_case_docs = []
            for doc in retrieved_docs:
                formatted_case_docs.append({
                    "id": doc.get("case_id", ""),
                    "issue": doc.get("issue", ""),
                    "chunk_text": doc.get("chunk_text", ""),  # chunk_text 필드를 직접 사용
                    "related_statutes": doc.get("statutes", "")
                })

            # case_docs를 JSON 문자열로 직렬화
            docs_json = json.dumps(formatted_case_docs, ensure_ascii=False)

            # 디버깅: 프롬프트에 포함될 데이터의 길이 확인
            self.logger.debug(f"User Query Length: {len(user_query)}")
            self.logger.debug(f"Case Docs JSON Length: {len(docs_json)}")

            # SPECIALTY_TAGS를 쉼표로 구분된 문자열로 변환
            tag_list_str = ", ".join(SPECIALTY_TAGS)
            

            invoked = self.chain.invoke({
                "user_query": user_query,
                "case_docs": docs_json,
                "tag_list": tag_list_str,
            })
            # RunnableSequence.invoke()는 마지막 LLM의 출력(보통 string 또는 {"text":…} 형태)을 그대로 돌려줍니다.
            raw_llm_response = invoked["text"] if isinstance(invoked, dict) and "text" in invoked else invoked

            # CotOutputParser를 사용하여 추론 과정과 결론을 분리합니다.
            cot_parsed_result = self.parser.parse(raw_llm_response)
            thought_process = cot_parsed_result["thought_process"]
            conclusion_text = cot_parsed_result["conclusion"]

            # parse_case_analysis_output을 사용하여 결론 텍스트를 구조화합니다.
            case_analysis_result = parse_case_analysis_output(conclusion_text)
            
            # 디버깅: CoT 결과와 태그 확인
            self.logger.debug(f"Raw conclusion text: {conclusion_text}")
            self.logger.debug(f"Parsed case_analysis_result: {vars(case_analysis_result)}")

            # 객관적 근거 기반 신뢰도 계산 (LLM이 생성한 값 대체)
            similarity_scores = [doc.get('_score', 0.5) for doc in retrieved_docs]
            calculated_confidence = self.confidence_calculator.calculate_confidence(
                query_case=user_query,
                retrieved_docs=retrieved_docs,
                similarity_scores=similarity_scores
            )
            
            # 계산된 신뢰도로 대체
            case_analysis_result.confidence = calculated_confidence
            self.logger.info(f"신뢰도 계산 완료: LLM 원본={case_analysis_result.confidence} -> 계산된 값={calculated_confidence}")

            # 법령 검증 및 보강 (새로운 기능)
            self._validate_and_enhance_statutes(case_analysis_result)

            # 변호사 추천 (옵션)
            recommended_lawyers = []
            if recommend_lawyers and self.lawyer_recommendation_service:
                try:
                    # CoT 결과에서 태그 추출 (tags 필드 활용)
                    extracted_tags = case_analysis_result.tags if hasattr(case_analysis_result, 'tags') else []
                    self.logger.info(f"Extracted tags from CoT result: {extracted_tags}")
                    
                    if extracted_tags:
                        self.logger.info(f"Using tags from CoT analysis: {extracted_tags}")
                        recommendation_result = await self.lawyer_recommendation_service.get_lawyer_recommendations_from_tags(
                            tags=extracted_tags,
                            limit=3
                        )
                        recommended_lawyers = recommendation_result.get("recommended_lawyers", [])
                        self.logger.info(f"Successfully got {len(recommended_lawyers)} lawyer recommendations")
                    else:
                        self.logger.warning("No tags found in CoT analysis result")
                        
                except Exception as e:
                    self.logger.error(f"Error in lawyer recommendation: {e}")
                    # 변호사 추천 실패해도 전체 분석 결과는 반환
                    recommended_lawyers = []

            # recommendedLawyers 필드를 CaseAnalysisResult에 설정
            case_analysis_result.recommendedLawyers = recommended_lawyers

            self.logger.info("Case analysis completed successfully")
            
            return {
                "case_analysis": case_analysis_result,
            }

    
    def _validate_and_enhance_statutes(self, case_analysis_result):
        """법령 검증 및 보강 파이프라인"""
        try:
            # 법령 검증 서비스 임포트 (순환 임포트 방지)
            from services.statute_validation_service import StatuteValidationService
            from app.api.schemas.statute import StatuteReference
            
            # 현재 결과에 statutes 필드가 있는지 확인
            if not hasattr(case_analysis_result, 'statutes'):
                # statutes 필드가 없으면 빈 리스트로 초기화
                case_analysis_result.statutes = []
                self.logger.warning("Case analysis result에 statutes 필드가 없어 초기화했습니다.")
                return
            
            self.logger.info(f"법령 검증 파이프라인 시작 - 기존 statutes: {case_analysis_result.statutes}")
            
            # 기존 statutes 필드 처리
            if hasattr(case_analysis_result, 'statutes'):
                original_statutes = case_analysis_result.statutes
                
                # statutes가 리스트 형태라면 각 항목을 문자열로 변환하여 검증
                if isinstance(original_statutes, list) and len(original_statutes) > 0:
                    self.logger.info(f"LLM이 생성한 법령 리스트 검증: {len(original_statutes)}개")
                    
                    # 리스트의 각 항목을 문자열로 변환
                    statute_strings = []
                    for i, item in enumerate(original_statutes):
                        self.logger.info(f"법령 항목 {i}: {item} (타입: {type(item)})")
                        if isinstance(item, dict) and 'code' in item:
                            # {"code": "형법", "article": "347조"} 형태
                            code = item['code']
                            article = item.get('article', '')
                            if article:
                                statute_str = f"{code} {article}"
                            else:
                                statute_str = code
                            statute_strings.append(statute_str)
                        elif hasattr(item, 'code'):
                            # StatuteReference 객체 형태
                            code = item.code
                            if hasattr(item, 'articles') and item.articles:
                                # articles가 리스트인 경우 첫 번째 항목 사용
                                article = item.articles[0] if item.articles else ''
                                if article:
                                    statute_str = f"{code} {article}"
                                else:
                                    statute_str = code
                            else:
                                statute_str = code
                            statute_strings.append(statute_str)
                        elif isinstance(item, str):
                            statute_strings.append(item)
                    
                    if statute_strings:
                        # 중복 제거
                        unique_statute_strings = list(dict.fromkeys(statute_strings))  # 순서 유지하면서 중복 제거
                        combined_statutes = ", ".join(unique_statute_strings)
                        self.logger.info(f"중복 제거 후 법령: {unique_statute_strings}")
                        self.logger.info(f"법령 검증 시작: {combined_statutes}")
                        
                        statute_validation_service = StatuteValidationService()
                        validation_results = statute_validation_service.validate_statutes(combined_statutes)
                        
                        # 검증된 법령을 새로운 형식으로 변환
                        enhanced_statutes = statute_validation_service.enhance_statutes_response(
                            validation_results, 
                            original_statutes
                        )
                        
                        # StatuteReference 객체 리스트로 변환
                        statute_references = []
                        
                        # 검증에 성공한 법령이 없어도 원본 법령명은 유지
                        if not enhanced_statutes:
                            self.logger.info("검증에 성공한 법령이 없지만 원본 법령명 유지")
                            for item in original_statutes:
                                if hasattr(item, 'code') and item.code:
                                    statute_ref = StatuteReference(
                                        code=item.code,
                                        articles=[],
                                        description=f"{item.code} (검증 실패하였으나 유지)",
                                        statute_id=None,
                                        department=None,
                                        confidence=0.5  # 낮은 신뢰도로 유지
                                    )
                                    statute_references.append(statute_ref)
                        else:
                            for enhanced in enhanced_statutes:
                                statute_ref = StatuteReference(
                                    code=enhanced.code,
                                    articles=enhanced.articles,
                                    description=enhanced.description,
                                    statute_id=enhanced.statute_id,
                                    department=enhanced.department,
                                    confidence=enhanced.confidence
                                )
                                statute_references.append(statute_ref)
                        
                        # 결과 업데이트
                        case_analysis_result.statutes = statute_references
                        self.logger.info(f"최종 법령 결과 설정: {len(statute_references)}개 - {[s.code for s in statute_references]}")
                        
                        # 통계 로깅
                        validation_stats = {
                            "total": len(validation_results),
                            "matched": len([r for r in validation_results if r.validation_result == "matched"]),
                            "corrected": len([r for r in validation_results if r.validation_result == "corrected"]),
                            "removed": len([r for r in validation_results if r.validation_result == "removed"]),
                            "suggested": len([r for r in validation_results if r.validation_result == "suggested"])
                        }
                        
                        self.logger.info(f"법령 검증 완료: {validation_stats}")
                        return
                    else:
                        # 빈 리스트로 설정
                        case_analysis_result.statutes = []
                        return
                
                # 빈 리스트라면 그대로 유지
                elif isinstance(original_statutes, list):
                    self.logger.info(f"빈 statutes 리스트 유지: {original_statutes}")
                    return
                
                # 문자열이라면 검증 진행
                elif isinstance(original_statutes, str) and original_statutes.strip():
                    statute_validation_service = StatuteValidationService()
                    
                    self.logger.info(f"법령 검증 시작: {original_statutes}")
                    
                    # 법령 검증 실행
                    validation_results = statute_validation_service.validate_statutes(original_statutes)
                    
                    # 검증된 법령을 새로운 형식으로 변환
                    enhanced_statutes = statute_validation_service.enhance_statutes_response(
                        validation_results, 
                        []  # 원본 statutes 정보가 문자열이므로 빈 리스트 전달
                    )
                    
                    # StatuteReference 객체 리스트로 변환
                    statute_references = []
                    for enhanced in enhanced_statutes:
                        statute_ref = StatuteReference(
                            code=enhanced.code,
                            articles=enhanced.articles,
                            description=enhanced.description,
                            statute_id=enhanced.statute_id,
                            department=enhanced.department,
                            confidence=enhanced.confidence
                        )
                        statute_references.append(statute_ref)
                    
                    # 결과 업데이트
                    case_analysis_result.statutes = statute_references
                    
                    # 통계 로깅
                    validation_stats = {
                        "total": len(validation_results),
                        "matched": len([r for r in validation_results if r.validation_result == "matched"]),
                        "corrected": len([r for r in validation_results if r.validation_result == "corrected"]),
                        "removed": len([r for r in validation_results if r.validation_result == "removed"]),
                        "suggested": len([r for r in validation_results if r.validation_result == "suggested"])
                    }
                    
                    self.logger.info(f"법령 검증 완료: {validation_stats}")
                    
                else:
                    # 빈 문자열이거나 None인 경우 빈 리스트로 설정
                    case_analysis_result.statutes = []
                    self.logger.info(f"원본 statutes가 비어있어 빈 리스트로 설정: {original_statutes}")
            
        except Exception as e:
            self.logger.error(f"법령 검증 및 보강 중 오류 발생: {e}")
            # 오류 발생 시 빈 리스트로 fallback
            if not hasattr(case_analysis_result, 'statutes'):
                case_analysis_result.statutes = []
        
        # 메서드 종료 시 최종 상태 로깅
        final_statutes_count = len(case_analysis_result.statutes) if hasattr(case_analysis_result, 'statutes') else 0
        self.logger.info(f"법령 검증 파이프라인 완료 - 최종 statutes 개수: {final_statutes_count}")
    

# 사용 예시 (기존 analyze_case 함수와 호환성을 위해)
async def analyze_case(case_text: str) -> dict:
    from llm.clients.langchain_client import Gpt4oMini
    from llm.models.model_loader import ModelLoader
    llm = Gpt4oMini()
    embedding_model = ModelLoader.get_embedding_model()
    cross_encoder_model = ModelLoader.get_cross_encoder_model()
    service = CaseAnalysisService(llm, embedding_model, cross_encoder_model)
    return await service.analyze_case(case_text)

if __name__ == "__main__":
    import asyncio
    sample_query = """
        {
            "case": {
            "title": "헬스장에서의 탈의실 잘못 진입 사건",
            "summary": "새해 목표를 다짐하며 헬스장에 등록한 후, 잘못 여자 탈의실에 들어간 사건이 발생했다. 상대방에게 사과를 했으나 헬스장 측에서 회원 등록 취소 요청을 받았고, 이후 상대방이 경찰에 신고했다는 소식을 들었다.",
            "fullText": "얼마 전 새해 목표를 다짐하며 동료와 함께 헬스장에 등록했다. 운동복으로 갈아입고 기분 좋게 샤워실을 찾다가, 문이 열린 채 여자 탈의실에 잘못 들어가고 말았다. 안에 누군가 있는 걸 보고 깜짝 놀라 급히 뛰어나왔지만, 다행히 얼굴을 보지 않아 상대방도 나를 알아보지 못한 상태였다. 얼굴이 화끈거려 동료에게 상황을 설명하고는 민망한 마음을 달래며 운동을 계속했다. 잠시 후 카운터 직원이 부름을 받고 와서 실수를 솔직히 인정하고 정중히 사과 의사를 전했다. 상대방은 대면을 원치 않는다며 곤란해했고, 나는 전화나 문자 등 원하는 방식으로 다시 사과하겠다고 했다. 헬스장 측에서는 며칠 뒤 연락을 주며 회원 등록을 취소해 달라는 요청을 받았다. 아쉬웠지만 상황을 받아들이고 환불 절차를 진행했다. 얼마간 시간이 흐른 뒤, 여자분이 경찰에 신고했다는 이야기를 전해 들으며 더욱 마음이 무거워졌다."
            }
        }
    """

    from llm.clients.langchain_client import Gpt4oMini
    from llm.models.model_loader import ModelLoader
    llm = Gpt4oMini()
    embedding_model = ModelLoader.get_embedding_model()
    cross_encoder_model = ModelLoader.get_cross_encoder_model()
    service = CaseAnalysisService(llm, embedding_model, cross_encoder_model)

    # Use asyncio.run to call the async analyze_case method
    data = json.loads(sample_query)
    full_text = data["case"]["fullText"]
    analysis = asyncio.run(service.analyze_case(full_text))

    # 1) Query는 이미 dict라면 직접 dumps
    print("== Query ==")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # 2) Conclusion: analysis가 dict이라면
    result = analysis['case_analysis']  # CaseAnalysisResult 인스턴스

    # 객체 내부를 dict로 변환
    case_dict = vars(result)  
    # 또는 case_dict = result.__dict__

    print("\n== Conclusion ==")
    print(json.dumps(case_dict, ensure_ascii=False, indent=2))
