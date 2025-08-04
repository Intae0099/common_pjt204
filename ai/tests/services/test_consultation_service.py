import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from app.api.schemas.consult import ConsultationRequest, CaseInfo
from services.consultation_service import ConsultationService
from llm.prompt_templates.consult_prompts import CORE_QUESTION_GENERATION_PROMPT, KEYWORD_TAG_GENERATION_PROMPT
from config.tags import SPECIALTY_TAGS

@pytest.fixture
def mock_llm_client():
    """Mock AsyncOpenAI client for testing LLM calls."""
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock()
    return mock

@pytest.fixture
def consultation_service(mock_llm_client):
    """Fixture for ConsultationService with mocked LLM client."""
    return ConsultationService(llm_client=mock_llm_client)

@pytest.fixture
def sample_consultation_request():
    """Sample ConsultationRequest for testing."""
    return ConsultationRequest(
        case=CaseInfo(
            title="음주운전 사건",
            summary="음주운전으로 인한 사고 발생",
            fullText="2023년 1월 1일, 김씨는 혈중알코올농도 0.08% 상태로 운전 중 신호 위반하여 사고를 냈습니다. 인명 피해는 없었으나 차량 파손이 심각합니다."
        ),
        desiredOutcome="벌금형 최소화 및 면허 취소 방지",
        weakPoints="음주운전 전과 1회, 사고 당시 혈중알코올농도 높음"
    )

class TestConsultationService:

    def test_format_application(self, consultation_service, sample_consultation_request):
        """Test _format_application method for correct data transformation."""
        formatted_app = consultation_service._format_application(sample_consultation_request)

        assert formatted_app["case"]["title"] == sample_consultation_request.case.title
        assert formatted_app["case"]["summary"] == sample_consultation_request.case.summary
        assert formatted_app["case"]["fullText"] == sample_consultation_request.case.fullText
        assert formatted_app["desiredOutcome"] == sample_consultation_request.desiredOutcome
        assert formatted_app["weakPoints"] == sample_consultation_request.weakPoints

    @pytest.mark.asyncio
    async def test_generate_questions_tags_from_llm_success(self, consultation_service, mock_llm_client):
        """Test _generate_questions_tags_from_llm for successful LLM call and parsing."""
        mock_llm_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({"questions": ["Q1", "Q2", "Q3"]})))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({"tags": ["T1", "T2", "T3"]})))]),
        ]

        application_data = {
            "case": {"fullText": "Test full text"},
            "desiredOutcome": "Test outcome"
        }

        questions, tags = await consultation_service._generate_questions_tags_from_llm(application_data)

        assert questions == ["Q1", "Q2", "Q3"]
        assert tags == ["T1", "T2", "T3"]

        # Verify LLM calls with correct prompts
        question_call_args = mock_llm_client.chat.completions.create.call_args_list[0].kwargs
        assert "Test full text" in question_call_args["messages"][1]["content"]
        assert "Test outcome" in question_call_args["messages"][1]["content"]
        assert question_call_args["response_format"] == {"type": "json_object"}

        tag_call_args = mock_llm_client.chat.completions.create.call_args_list[1].kwargs
        assert "Test full text" in tag_call_args["messages"][1]["content"]
        assert all(tag in tag_call_args["messages"][1]["content"] for tag in SPECIALTY_TAGS[:3]) # Check some tags are passed
        assert tag_call_args["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_generate_questions_tags_from_llm_parsing_failure(self, consultation_service, mock_llm_client):
        """Test _generate_questions_tags_from_llm for LLM call success but JSON parsing failure."""
        mock_llm_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content="invalid json"))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content="another invalid json"))]),
        ]

        application_data = {
            "case": {"fullText": "Test full text"},
            "desiredOutcome": "Test outcome"
        }

        questions, tags = await consultation_service._generate_questions_tags_from_llm(application_data)

        assert questions == []
        assert tags == []

    @pytest.mark.asyncio
    async def test_generate_questions_tags_from_llm_llm_failure(self, consultation_service, mock_llm_client):
        """Test _generate_questions_tags_from_llm for LLM call failure (exception)."""
        mock_llm_client.chat.completions.create.side_effect = Exception("LLM API Error")

        application_data = {
            "case": {"fullText": "Test full text"},
            "desiredOutcome": "Test outcome"
        }

        questions, tags = await consultation_service._generate_questions_tags_from_llm(application_data)

        assert questions == []
        assert tags == []

    @pytest.mark.asyncio
    async def test_create_application_and_questions_integration(self, consultation_service, mock_llm_client, sample_consultation_request):
        """Test the public method create_application_and_questions integration."""
        mock_llm_client.chat.completions.create.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({"questions": ["IntQ1", "IntQ2", "IntQ3"]})))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({"tags": ["IntT1", "IntT2", "IntT3"]})))]),
        ]

        result = await consultation_service.create_application_and_questions(sample_consultation_request)

        assert "application" in result
        assert result["application"]["case"]["title"] == sample_consultation_request.case.title
        assert result["questions"] == ["IntQ1", "IntQ2", "IntQ3"]
        assert result["tags"] == ["IntT1", "IntT2", "IntT3"]
