import json
from typing import Any, Dict, List, Tuple, Optional

from openai import AsyncOpenAI

from app.api.schemas.consult import ConsultationRequest, ApplicationCase, ApplicationData
from llm.prompt_templates.consult_prompts import (
    CORE_QUESTION_GENERATION_PROMPT,
    KEYWORD_TAG_GENERATION_PROMPT,
    APPLICATION_FORMAT_PROMPT
)
from config.tags import SPECIALTY_TAGS
from services.external_api_client import ExternalAPIClient
from utils.logger import LoggerMixin
from utils.exceptions import handle_service_exceptions


class ConsultationService(LoggerMixin):
    """
    상담 신청서 생성 및 관련 AI 기능을 처리하는 서비스 클래스입니다.
    """
    def __init__(self, llm_client: AsyncOpenAI, external_api_client: Optional[ExternalAPIClient] = None):
        self.llm_client = llm_client
        self.external_api_client = external_api_client
        self.logger.info("ConsultationService initialized")

    def _format_application(self, request: ConsultationRequest) -> Dict[str, Any]:
        """
        원본 Pydantic 객체에서 model_dump한 JSON을 LLM에 전달하여
        주요 필드만 추려낸 가독성 높은 application dict로 변환합니다.
        실패 시에는 최소 필드만 수동 매핑하여 반환합니다.
        """
        # 1) raw application 데이터 생성
        case_obj = ApplicationCase(
            title=request.case.title,
            summary=request.case.summary,
            fullText=request.case.fullText,
        )
        raw_app = ApplicationData(
            case=case_obj,
            weakPoints=request.weakPoints,
            desiredOutcome=request.desiredOutcome,
        ).model_dump()

        # 2) LLM 호출
        try:
            prompt = APPLICATION_FORMAT_PROMPT.format(raw_json=json.dumps(raw_app, ensure_ascii=False))
            resp = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a JSON formatting assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            formatted = json.loads(resp.choices[0].message.content)
            # 검증: 필수 키가 모두 있는지 확인
            if all(k in formatted for k in ("case", "weakPoints", "desiredOutcome")):
                return formatted
        except Exception:
            # LLM 포맷 실패 시 수동 매핑으로 fallback
            pass

        # 3) 수동 매핑 fallback
        return {
            "case": {
                "title": raw_app["case"]["title"],
                "summary": raw_app["case"]["summary"],
                "fullText": raw_app["case"]["fullText"],
            },
            "weakPoints": raw_app.get("weakPoints", ""),
            "desiredOutcome": raw_app.get("desiredOutcome", ""),
        }

    async def _call_llm_and_parse(
        self, prompt: str, field: str
    ) -> List[str]:
        """
        LLM 호출 후 JSON 파싱을 수행하고, 지정된 key(field)의 리스트를 반환합니다.
        실패 시 빈 리스트 반환.
        """
        try:
            response = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You output strict JSON."},
                    {"role": "user", "content": prompt},
                ],
            )
            data = json.loads(response.choices[0].message.content)
            return data.get(field, []) if isinstance(data.get(field), list) else []
        except Exception:
            return []

    async def _generate_questions_tags_from_llm(
        self, application: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """
        LLM 호출을 통해 핵심 질문과 키워드 태그를 생성·파싱하여 반환합니다.
        실패 시 빈 리스트 반환.
        """
        full_text = application["case"]["fullText"]
        desired = application.get("desiredOutcome", "")

        q_prompt = CORE_QUESTION_GENERATION_PROMPT.format(
            fullText=full_text,
            desiredOutcome=desired,
        )
        questions = await self._call_llm_and_parse(q_prompt, "questions")

        t_prompt = KEYWORD_TAG_GENERATION_PROMPT.format(
            fullText=full_text,
            specialty_tags=", ".join(SPECIALTY_TAGS),
        )
        tags = await self._call_llm_and_parse(t_prompt, "tags")

        return questions, tags

    @handle_service_exceptions("태그 ID 변환 중 오류가 발생했습니다.")
    async def _convert_tags_to_ids(self, tags: List[str]) -> List[int]:
        """
        태그 문자열을 외부 API를 통해 태그 ID로 변환합니다.
        
        Args:
            tags: 태그 문자열 리스트
            
        Returns:
            태그 ID 리스트 (실패 시 빈 리스트)
        """
        if not tags or not self.external_api_client:
            self.logger.warning("No tags to convert or external API client not available")
            return []
        
        try:
            self.logger.info(f"Converting {len(tags)} tags to IDs: {tags}")
            tag_ids = await self.external_api_client.resolve_tag_ids(tags)
            self.logger.info(f"Successfully converted to {len(tag_ids)} tag IDs: {tag_ids}")
            return tag_ids
        except Exception as e:
            self.logger.error(f"Failed to convert tags to IDs: {e}")
            return []

    async def create_application_and_questions(
        self, request: ConsultationRequest
    ) -> Dict[str, Any]:
        """
        상담 신청서(application), 핵심 질문, 태그 ID를 생성하여 반환합니다.
        """
        # application: LLM 포맷 또는 수동 매핑
        application = self._format_application(request)
        questions, tag_strings = await self._generate_questions_tags_from_llm(application)

        # 태그 문자열을 태그 ID로 변환
        tag_ids = await self._convert_tags_to_ids(tag_strings)

        return {
            "application": application,
            "questions": questions,
            "tags": tag_ids,  # 숫자 배열로 변경
        }

