import json
import logging
from typing import Dict, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from llm.prompt_templates.structuring_prompts import STRUCTURING_PROMPT

logger = logging.getLogger(__name__)

class StructuringService:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt = STRUCTURING_PROMPT

    async def structure_case(self, free_text: str) -> Dict[str, str]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} to structure case.")
                chain = self.prompt | self.llm
                response = await chain.ainvoke({"free_text": free_text})
                
                response_content = response.content if hasattr(response, 'content') else response
                # Assuming the LLM response is a string that needs to be parsed as JSON
                structured_data = json.loads(response_content)
                
                # Validate the structure
                if not all(key in structured_data for key in ["title", "summary", "fullText"]):
                    raise ValueError("LLM response missing required keys: title, summary, fullText")
                
                return structured_data

            except json.JSONDecodeError as e:
                logger.warning(f"JSON decoding failed on attempt {attempt + 1}: {e}")
            except ValueError as e:
                logger.warning(f"Validation failed on attempt {attempt + 1}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Failed to structure case.")
                raise RuntimeError("Failed to structure case after multiple retries.")

        raise RuntimeError("Should not reach here")
