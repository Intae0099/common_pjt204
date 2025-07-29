import logging
from typing import Dict, Any

from langchain_core.language_models import BaseChatModel

from llm.prompt_templates.structuring_prompts import STRUCTURING_PROMPT
from llm.structuring_parser import StructuringParser  # StructuringParser 임포트

logger = logging.getLogger(__name__)

class StructuringService:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = STRUCTURING_PROMPT
        self.parser = StructuringParser()  # 파서 인스턴스 생성

    async def structure_case(self, free_text: str) -> Dict[str, str]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} to structure case.")
                chain = self.prompt | self.llm
                response = await chain.ainvoke({"free_text": free_text})
                
                response_content = response.content if hasattr(response, 'content') else response
                
                # StructuringParser를 사용하여 LLM 응답 파싱 및 보정
                structured_data = self.parser.parse(response_content)
                
                return structured_data

            except Exception as e:
                logger.error(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Failed to structure case.")
                raise RuntimeError("Failed to structure case after multiple retries.")

        raise RuntimeError("Should not reach here")
