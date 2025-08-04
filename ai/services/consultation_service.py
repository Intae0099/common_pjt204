import json
from typing import Any, Dict, List, Tuple

from openai import AsyncOpenAI

from app.api.schemas.consult import ConsultationRequest, ApplicationCase, ApplicationData
from llm.prompt_templates.consult_prompts import (
    CORE_QUESTION_GENERATION_PROMPT,
    KEYWORD_TAG_GENERATION_PROMPT,
    APPLICATION_FORMAT_PROMPT
)
from config.tags import SPECIALTY_TAGS


class ConsultationService:
    """
    상담 신청서 생성 및 관련 AI 기능을 처리하는 서비스 클래스입니다.
    """
    def __init__(self, llm_client: AsyncOpenAI):
        self.llm_client = llm_client

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

    async def create_application_and_questions(
        self, request: ConsultationRequest
    ) -> Dict[str, Any]:
        """
        상담 신청서(application), 핵심 질문, 태그를 생성하여 반환합니다.
        """
        # application: LLM 포맷 또는 수동 매핑
        application = self._format_application(request)
        questions, tags = await self._generate_questions_tags_from_llm(application)

        return {
            "application": application,
            "questions": questions,
            "tags": tags,
        }

