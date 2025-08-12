import pytest
from unittest.mock import MagicMock, AsyncMock
import json

from services.consultation_service import ConsultationService
from app.api.schemas.consult import ConsultationRequest, CaseInfo


class MockAsyncOpenAI:
    def __init__(self):
        self.chat = MockAsyncChat()


class MockAsyncChat:
    def __init__(self):
        self.completions = MockAsyncCompletions()


class MockAsyncCompletions:
    async def create(self, **kwargs):
        model = kwargs.get('model', 'gpt-4o-mini')
        messages = kwargs.get('messages', [])
        
        # 메시지 내용에 따라 다른 응답 반환
        last_message = messages[-1]['content'] if messages else ""
        
        if "핵심 질문" in last_message or "CORE_QUESTION" in last_message:
            response_content = json.dumps({
                "questions": [
                    "계약서에 명시된 의무사항을 이행하셨나요?",
                    "상대방의 계약 위반 사실을 증명할 수 있는 자료가 있나요?",
                    "발생한 손해의 구체적인 금액을 산정하셨나요?"
                ]
            }, ensure_ascii=False)
        elif "키워드" in last_message or "KEYWORD_TAG" in last_message:
            response_content = json.dumps({
                "keywords": ["계약위반", "손해배상", "민사소송"],
                "tags": ["민사", "계약"]
            }, ensure_ascii=False)
        elif "APPLICATION_FORMAT" in last_message:
            response_content = json.dumps({
                "title": "계약 위반에 따른 손해배상 청구",
                "summary": "계약 상대방의 의무 불이행으로 인한 손해배상 분쟁",
                "description": "구체적인 계약 위반 사항과 발생한 손해에 대한 배상 청구 상담",
                "legalBasis": "민법 제390조 (채무불이행과 손해배상)",
                "urgencyLevel": "보통"
            }, ensure_ascii=False)
        else:
            response_content = "기본 응답"
        
        return MagicMock(choices=[MagicMock(message=MagicMock(content=response_content))])


@pytest.fixture
def mock_openai_client():
    return MockAsyncOpenAI()


@pytest.fixture
def consultation_service(mock_openai_client):
    return ConsultationService(mock_openai_client)


@pytest.fixture
def sample_request():
    return ConsultationRequest(
        case=CaseInfo(
            title="계약 분쟁 상담",
            summary="계약 위반으로 인한 손해 발생",
            fullText="회사와의 계약에서 상대방이 의무를 이행하지 않아 손해가 발생했습니다."
        ),
        desiredOutcome="손해배상 청구",
        weakPoints="계약서 미비"
    )


@pytest.mark.asyncio
async def test_상담신청서_생성_성공(consultation_service, sample_request):
    """상담 신청서와 관련 질문을 성공적으로 생성하는지 테스트"""
    result = await consultation_service.create_application_and_questions(sample_request)
    
    # 기본 구조 확인
    assert "application" in result
    assert "questions" in result  
    assert "tags" in result
    
    # 신청서 내용 확인
    assert result["application"]["case"]["title"] == "계약 분쟁 상담"
    assert result["application"]["desiredOutcome"] == "손해배상 청구"
    assert result["application"]["weakPoints"] == "계약서 미비"
    
    # AI 생성 콘텐츠 확인
    assert isinstance(result["questions"], list)
    assert isinstance(result["tags"], list)


@pytest.mark.asyncio
async def test_신청서_포맷_처리_성공(consultation_service, sample_request):
    """신청서 포맷팅이 정상적으로 동작하는지 테스트"""
    # _format_application은 private 메서드이지만 테스트에서 직접 호출
    formatted_app = consultation_service._format_application(sample_request)
    
    assert "case" in formatted_app
    assert "desiredOutcome" in formatted_app
    assert "weakPoints" in formatted_app
    
    assert formatted_app["case"]["title"] == "계약 분쟁 상담"
    assert formatted_app["desiredOutcome"] == "손해배상 청구"


@pytest.mark.asyncio
async def test_빈_사건_정보_처리(consultation_service):
    """사건 정보가 최소한일 때도 처리가 되는지 테스트"""
    minimal_request = ConsultationRequest(
        case=CaseInfo(title="간단 상담", summary="", fullText=""),
        desiredOutcome="일반상담",
        weakPoints=""
    )
    
    result = await consultation_service.create_application_and_questions(minimal_request)
    
    assert result["application"]["case"]["title"] == "간단 상담"
    assert result["application"]["desiredOutcome"] == "일반상담"
    # AI 처리도 정상적으로 진행되어야 함 (빈 리스트라도 반환)
    assert "questions" in result
    assert "tags" in result


@pytest.mark.asyncio
async def test_LLM_호출_성공시_응답_파싱(consultation_service, sample_request):
    """LLM이 유효한 JSON을 반환할 때 올바르게 파싱되는지 테스트"""
    result = await consultation_service.create_application_and_questions(sample_request)
    
    # Mock이 설정한 응답이 올바르게 파싱되었는지 확인
    assert len(result["questions"]) > 0
    assert "계약서" in result["questions"][0]
    assert len(result["tags"]) > 0
    assert "민사" in result["tags"]


@pytest.mark.asyncio  
async def test_LLM_응답_파싱_오류_처리(consultation_service, sample_request):
    """LLM 응답 파싱 오류 시 빈 리스트 반환하는지 테스트"""
    # 잘못된 JSON을 반환하는 Mock 설정
    consultation_service.llm_client.chat.completions.create = AsyncMock(
        return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="잘못된 JSON"))])
    )
    
    # 파싱 오류가 발생해도 기본값(빈 리스트)이 반환되어야 함
    result = await consultation_service.create_application_and_questions(sample_request)
    
    # 신청서는 수동 매핑으로 생성되어야 함
    assert "application" in result
    assert result["application"]["case"]["title"] == "계약 분쟁 상담"
    
    # 질문과 태그는 빈 리스트가 반환되어야 함
    assert result["questions"] == []
    assert result["tags"] == []


@pytest.mark.asyncio
async def test_프라이빗_메서드_질문_태그_생성(consultation_service):
    """_generate_questions_tags_from_llm 메서드가 올바르게 동작하는지 테스트"""
    test_application = {
        "case": {
            "fullText": "계약 위반으로 인한 손해 발생",
            "title": "테스트 사건",
            "summary": "테스트 요약"
        },
        "desiredOutcome": "손해배상"
    }
    
    questions, tags = await consultation_service._generate_questions_tags_from_llm(test_application)
    
    assert isinstance(questions, list)
    assert isinstance(tags, list)
    # Mock 응답에 따라 결과가 생성되어야 함
    assert len(questions) > 0
    assert len(tags) > 0