from langchain.chains import LLMChain
from langchain.llms.base import LLM
from typing import List, Dict
import json

from config.tags import SPECIALTY_TAGS
from llm.llm_response_parser import CotOutputParser, parse_case_analysis_output, CaseAnalysisResult
from llm.prompt_templates import get_cot_prompt
from services.search_service import search_cases

class CaseAnalysisService:
    def __init__(self, llm: LLM):
        """
        LLM 객체를 주입받아 초기화합니다.

        Args:
            llm (LLM): LangChain의 LLM 인터페이스를 구현한 객체
        """
        self.llm = llm
        self.prompt_template = get_cot_prompt()
        self.parser = CotOutputParser()
        # `prompt | llm` 로 RunnableSequence를 만듭니다. (LangChain 0.1.17 이상 권장 방식)
        self.chain = self.prompt_template | self.llm

    def analyze_case(
            self,
            user_query: str,
            top_k_docs: int = 5, # RAG를 위한 top_k 인자 추가
        ) -> dict:
            """
            Args:
                user_query: 사용자가 물어본 질문
                top_k_docs: 검색할 관련 판례의 개수
            """
            # 1. 관련 판례 검색 (RAG)
            retrieved_docs = search_cases(user_query, top_k=top_k_docs)

            # 2. 검색된 판례를 LLM 입력 형식에 맞게 변환
            # search_cases의 결과는 {'case_id': str, 'summary': str, 'full_text': str}
            # LLM은 {"id": "...", "text": "..."} 형태를 기대
            formatted_case_docs = []
            for doc in retrieved_docs:
                formatted_case_docs.append({
                    "id": doc.get("case_id", ""),
                    "issue": doc.get("issue", ""), # issue를 name으로 사용
                    "text": doc.get("chunk_text", "")
                })

            # case_docs를 JSON 문자열로 직렬화
            docs_json = json.dumps(formatted_case_docs, ensure_ascii=False)

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

            return {
                "case_analysis": case_analysis_result,
            }

# 사용 예시 (기존 analyze_case 함수와 호환성을 위해)
def analyze_case(case_text: str) -> dict:
    from llm.clients.langchain_client import Gpt4oMini
    llm = Gpt4oMini()
    service = CaseAnalysisService(llm)
    return service.analyze_case(case_text)

if __name__ == "__main__":
    sample_query = """
        {
        "case": {
            "title": "SSAFY 보안 서약서 위반 및 교육 자료 무단 게시 사건",
            "summary": "SSAFY 입과 시 보안 서약서에 서명한 후 교육용 프로젝트 화면 캡쳐를 블로그에 무단 공개함",
            "fullText": "SSAFY 과정에 참여한 사용자는 입과 시 보안 서약서를 작성하여 교육 자료나 코드, 화면을 외부에 공개하지 않을 것을 약속했습니다. 그러나 중간 프로젝트 발표를 준비하던 중 프로젝트 실행 화면과 소스 코드 일부를 캡쳐하여 개인 블로그에 게시했고, 안내된 가이드라인과 서약서 조항을 명백히 위반했습니다. 이로 인해 교육 기관과 동료 학습자의 권리가 침해될 수 있다는 우려가 제기되었으며, 이를 문제 삼을 경우 즉 본보기가 되어 고소 당하는 것을 걱정하고 있다"
        }
        }
    """

    from llm.clients.langchain_client import Gpt4oMini
    llm = Gpt4oMini()
    service = CaseAnalysisService(llm)

    analysis = service.analyze_case(sample_query)
    print("== Thought Process ==")
    print(analysis["thought_process"])
    print("\n== Conclusion ==")
    print(analysis["case_analysis"])
