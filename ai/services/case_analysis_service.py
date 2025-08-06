from langchain.chains import LLMChain
from langchain.llms.base import LLM
from typing import List, Dict
import json

from config.tags import SPECIALTY_TAGS
from config.settings import get_llm_settings
from llm.llm_response_parser import CotOutputParser, parse_case_analysis_output, CaseAnalysisResult
from llm.prompt_templates import get_cot_prompt
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel
from services.search_service import SearchService
from utils.logger import LoggerMixin
from utils.exceptions import handle_service_exceptions, LLMError

class CaseAnalysisService(LoggerMixin):
    def __init__(self, llm: LLM, search_service: SearchService):
        """
        LLM 객체와 검색 서비스를 주입받아 초기화합니다.

        Args:
            llm (LLM): LangChain의 LLM 인터페이스를 구현한 객체
            search_service (SearchService): 검색 서비스 인스턴스
        """
        self.llm = llm
        self.search_service = search_service
        self.prompt_template = get_cot_prompt()
        self.parser = CotOutputParser()
        # `prompt | llm` 로 RunnableSequence를 만듭니다. (LangChain 0.1.17 이상 권장 방식)
        self.chain = self.prompt_template | self.llm

    @handle_service_exceptions("법률 분석 처리 중 오류가 발생했습니다.")
    async def analyze_case(
            self,
            user_query: str,
            top_k_docs: int = 5, # RAG를 위한 top_k 인자 추가
        ) -> dict:
            """
            Args:
                user_query: 사용자가 물어본 질문
                top_k_docs: 검색할 관련 판례의 개수
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
                    "text": doc.get("chunk_text", "")  # chunk_text 필드를 직접 사용
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

            self.logger.info("Case analysis completed successfully")
            return {
                "case_analysis": case_analysis_result,
            }

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
