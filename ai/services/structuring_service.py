from typing import Dict, Any
import time

from langchain_core.language_models import BaseChatModel

from config.settings import get_llm_settings
from llm.prompt_templates.structuring_prompts import STRUCTURING_PROMPT
from llm.structuring_parser import StructuringParser
from utils.logger import LoggerMixin
from utils.exceptions import handle_service_exceptions, LLMError

class StructuringService(LoggerMixin):
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = STRUCTURING_PROMPT
        self.parser = StructuringParser()  # 파서 인스턴스 생성

    @handle_service_exceptions("사건 구조화 처리 중 오류가 발생했습니다.")
    async def structure_case(self, free_text: str) -> Dict[str, str]:
        llm_settings = get_llm_settings()
        max_retries = llm_settings.max_retries
        
        start_time = self.log_start("사건 구조화")
        
        for attempt in range(max_retries):
            try:
                attempt_start = self.log_start(f"구조화 시도 {attempt + 1}/{max_retries}")
                
                chain = self.prompt | self.llm
                response = await chain.ainvoke({"free_text": free_text})
                
                response_content = response.content if hasattr(response, 'content') else response
                
                # StructuringParser를 사용하여 LLM 응답 파싱 및 보정
                structured_data = self.parser.parse(response_content)
                
                self.log_complete(f"구조화 시도 {attempt + 1}", attempt_start)
                self.log_complete("사건 구조화", start_time)
                return structured_data

            except Exception as e:
                attempt_duration = (time.time() - attempt_start) * 1000
                self.logger.warning(f"구조화 시도 {attempt + 1} 실패 [{attempt_duration:.0f}ms]: {e}")
                
                if attempt == max_retries - 1:
                    total_duration = (time.time() - start_time) * 1000
                    self.logger.error(f"최대 재시도 횟수 도달. 사건 구조화 실패 [{total_duration:.0f}ms]")
                    raise LLMError(
                        "사건 구조화에 실패했습니다.",
                        details={"attempts": max_retries, "last_error": str(e)},
                        original_exception=e
                    )
        
        # 이 코드는 실행되지 않아야 함
        raise LLMError("예상치 못한 오류가 발생했습니다.")
