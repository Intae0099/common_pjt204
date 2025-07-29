import pytest
import logging
from llm.structuring_parser import StructuringParser

# 로거 설정 (테스트 시 WARNING 로그 캡처를 위해)
@pytest.fixture
def caplog_fixture(caplog):
    caplog.set_level(logging.WARNING)
    return caplog

@pytest.fixture
def parser():
    return StructuringParser()

def test_normal_json_parsing(parser):
    """정상적인 JSON 입력에 대해 올바르게 파싱하는지 테스트"""
    json_input = """
    {
        "title": "사건명: 김철수 폭행 사건",
        "summary": "김철수가 박영희를 폭행하여 상해를 입힌 사건. 경찰 조사 결과 쌍방 폭행으로 밝혀짐.",
        "fullText": "2023년 5월 10일, 서울 강남구에서 김철수와 박영희 사이에 시비가 붙어 폭행 사건이 발생했다. 박영희는 전치 2주의 상해를 입었으며, 김철수도 경미한 부상을 입었다. 경찰은 CCTV 분석과 목격자 진술을 토대로 수사를 진행 중이다."
    }
    """
    result = parser.parse(json_input)
    assert result["title"] == "사건명: 김철수 폭행 사건"
    assert result["summary"] == "김철수가 박영희를 폭행하여 상해를 입힌 사건. 경찰 조사 결과 쌍방 폭행으로 밝혀짐."
    assert result["fullText"] == "2023년 5월 10일, 서울 강남구에서 김철수와 박영희 사이에 시비가 붙어 폭행 사건이 발생했다. 박영희는 전치 2주의 상해를 입었으며, 김철수도 경미한 부상을 입었다. 경찰은 CCTV 분석과 목격자 진술을 토대로 수사를 진행 중이다."

def test_malformed_json_parsing_with_recovery(parser, caplog_fixture):
    """잘못된 JSON 입력에 대해 복구 로직이 작동하고 WARNING 로그를 남기는지 테스트"""
    malformed_json_input = """
    {
        "title": "사건명: 이영희 절도 사건",
        "summary": "이영희가 마트에서 물건을 훔치다 적발된 사건. 초범이며 반성하는 태도를 보임.",
        "fullText": "2023년 6월 1일, 이영희는 서울 송파구의 한 마트에서 샴푸와 비누를 훔치다 보안요원에게 붙잡혔다. 이영희는 생활고를 호소하며 선처를 바라고 있다."
    """ # 닫는 중괄호 누락
    result = parser.parse(malformed_json_input)

    assert "JSON 파싱 실패" in caplog_fixture.text
    assert "복구 모드 진입" in caplog_fixture.text
    assert result["title"] != ""
    assert result["summary"] != ""
    assert result["fullText"] != ""
    assert result["fullText"] == parser._trim_whitespace(malformed_json_input) # 원시 입력이 fullText로 사용되었는지 확인

def test_empty_input(parser, caplog_fixture):
    """빈 문자열 입력에 대해 기본값으로 보정하는지 테스트"""
    result = parser.parse("")

    assert "JSON 파싱 실패" in caplog_fixture.text
    assert "'fullText' 키 누락 또는 비어있음" in caplog_fixture.text
    assert "'summary' 키 누락 또는 비어있음" in caplog_fixture.text
    assert "'title' 키 누락 또는 비어있음" in caplog_fixture.text

    assert result["title"] == parser.DEFAULT_TITLE
    assert result["summary"] == ""
    assert result["fullText"] == ""

def test_summary_length_limit(parser):
    """summary 길이가 제한을 초과하지 않는지 테스트"""
    long_summary_text = "a" * (parser.SUMMARY_MAX_LEN + 50)
    json_input = f"{{\"title\": \"Test\", \"summary\": \"{long_summary_text}\", \"fullText\": \"Full text\"}}"
    result = parser.parse(json_input)
    assert len(result["summary"]) == parser.SUMMARY_MAX_LEN

def test_trimming(parser):
    """트리밍 기능이 올바르게 작동하는지 테스트"""
    text_with_whitespace = "\n\n  Hello World  \n\n"
    # JSON 내부의 값은 파서가 트리밍해야 함을 테스트
    json_input = f"{{\"title\": \" {text_with_whitespace} \", \"summary\": \" {text_with_whitespace} \", \"fullText\": \" {text_with_whitespace} \"}}"
    result = parser.parse(json_input)
    assert result["title"] == "Hello World"
    assert result["summary"] == "Hello World"
    assert result["fullText"] == "Hello World"

def test_fulltext_only_input(parser, caplog_fixture):
    """fullText만 있는 JSON 입력에 대해 나머지 키가 보정되는지 테스트"""
    json_input = """
    {
        "fullText": "이것은 fullText만 있는 입력입니다. 요약과 제목이 생성되어야 합니다."
    }
    """
    result = parser.parse(json_input)

    assert "'summary' 키 누락 또는 비어있음" in caplog_fixture.text
    assert "'title' 키 누락 또는 비어있음" in caplog_fixture.text

    assert result["title"] == "이것은 fullText만 있는 입력입니다."
    assert result["summary"].startswith("이것은 fullText만 있는 입력입니다.")
    assert result["fullText"] == "이것은 fullText만 있는 입력입니다. 요약과 제목이 생성되어야 합니다."

def test_truncated_json_input(parser, caplog_fixture):
    """중간에 잘린 JSON 입력에 대해 복구 로직이 작동하는지 테스트"""
    truncated_json = """
    {
        "title": "잘린 JSON 테스트",
        "summary": "이것은 잘린 요약입니다.",
        "fullText": "이것은 잘린 전문입니다. 중간에 끊겼습니다.
    """ # 의도적으로 잘린 JSON (missing closing quote for fullText and closing brace for JSON)
    result = parser.parse(truncated_json)

    assert "JSON 파싱 실패" in caplog_fixture.text
    assert "복구 모드 진입" in caplog_fixture.text
    assert result["title"] != ""
    assert result["summary"] != ""
    assert result["fullText"] != ""
    assert result["fullText"] == parser._trim_whitespace(truncated_json)

def test_non_string_input_to_trim(parser):
    """_trim_whitespace에 문자열이 아닌 값이 들어왔을 때 빈 문자열을 반환하는지 테스트"""
    assert parser._trim_whitespace(None) == ""
    assert parser._trim_whitespace(123) == ""
    assert parser._trim_whitespace([]) == ""
