from typing import Any, List, Mapping, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

# This relative import is correct for modules in the same directory
from .openai_client import call_gpt4o


class Gpt4oMini(LLM):
    """LangChain의 LLM 인터페이스를 구현한 GPT-4o-mini 클라이언트입니다."""

    temperature: float = 0.0
    max_tokens: int = 2048

    @property
    def _llm_type(self) -> str:
        return "gpt-4o-mini"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """GPT-4o-mini 모델을 호출하여 응답을 반환합니다."""
        messages = [{"role": "user", "content": prompt}]
        return call_gpt4o(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """모델의 식별 파라미터를 반환합니다."""
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
