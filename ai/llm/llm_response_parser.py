import re
from typing import Dict, Any
from langchain.schema import BaseOutputParser

class CotOutputParser(BaseOutputParser):
    """CoT(Chain-of-Thought) 응답을 파싱하여 중간 추론 과정과 최종 결론을 분리합니다."""

    def parse(self, text: str) -> Dict[str, Any]:
        """정규표현식을 사용하여 LLM의 응답에서 추론 과정과 결론을 추출합니다."""
        # "결론:" 부분을 기준으로 텍스트를 분리합니다.
        match = re.search(r"결론: (.*)", text, re.DOTALL)
        if match:
            conclusion = match.group(1).strip()
            thought_process = text[:match.start()].strip()
        else:
            # "결론:"이 없는 경우, 전체를 추론 과정으로 간주하고 결론은 비워둡니다.
            conclusion = ""
            thought_process = text.strip()

        return {
            "thought_process": thought_process,
            "conclusion": conclusion,
        }
