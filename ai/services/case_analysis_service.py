from langchain.chains import LLMChain
from langchain.llms.base import LLM
from typing import List, Dict
import json




from ai.llm.llm_response_parser import CotOutputParser, parse_case_analysis_output, CaseAnalysisResult
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
        # `prompt | llm` 로 RunnableSequence를 만듭니다. (LangChain 0.1.17 이상 권장 방식) :contentReference[oaicite:0]{index=0}
        self.chain = self.prompt_template | self.llm

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

            invoked = self.chain.invoke({
                "user_query": user_query,
                "case_docs": docs_json,
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
                "thought_process": thought_process,
                "case_analysis": case_analysis_result
            }

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
    print(analysis["case_analysis"])