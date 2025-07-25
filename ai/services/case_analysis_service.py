from langchain.chains import LLMChain
from langchain.llms.base import LLM
from typing import List, Dict
import json

from ai.llm.llm_response_parser import CotOutputParser
from ai.llm.prompt_templates import get_cot_prompt

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
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template,
            output_parser=self.parser
        )

    def analyze_case(
            self,
            user_query: str,
            case_docs: List[Dict[str, str]],  # 예: [{"id": "2019다1234", "text": "…"}]
        ) -> dict:
            """
            Args:
                user_query: 사용자가 물어본 질문
                case_docs: 관련 판례 목록 (id, name, text 등)
            """
            # case_docs를 JSON 문자열로 직렬화
            docs_json = json.dumps(case_docs, ensure_ascii=False)

            # 실제 플레이스홀더 이름과 맞춰서 딕셔너리로 넘김
            result = self.chain.invoke({
                "user_query": user_query,
                "case_docs": docs_json,
            })

            # CotOutputParser가 파싱한 dict가 result["text"]에 담겨 있음
            return result["text"]

# 사용 예시 (기존 analyze_case 함수와 호환성을 위해)
def analyze_case(case_text: str) -> dict:
    from ai.llm import Gpt4oMini
    llm = Gpt4oMini()
    service = CaseAnalysisService(llm)
    return service.analyze_case(case_text)

if __name__ == "__main__":
    sample_query = """
    {
    "case": {
        "title": "회사 볼펜 무단 반출 분쟁",
        "summary": "회사에서 볼펜 2개를 무단으로 가져간 뒤 반납을 두고 회사와 언쟁이 발생함",
        "fullText": "사용자가 회사에서 볼펜 2개를 무단으로 가져나왔고, 회사가 이를 다시 가져다 놓으라고 요구하자 양측 간에 언쟁이 발생했습니다. 자존심이 상한 사용자는 이 문제를 어떻게 해결해야 할지 고민하고 있습니다."
    }
    }"""
    sample_docs = [
        {"id": "2019다1234", "name": "대법원 2019다1234", "text": "…판례 전문…"},
        {"id": "2020다5678", "name": "대법원 2020다5678", "text": "…판례 전문…"},
    ]

    from ai.llm import Gpt4oMini
    llm = Gpt4oMini()
    service = CaseAnalysisService(llm)

    analysis = service.analyze_case(sample_query, sample_docs)
    print("== Thought Process ==")
    print(analysis["thought_process"])
    print("\n== Conclusion ==")
    print(analysis["conclusion"])