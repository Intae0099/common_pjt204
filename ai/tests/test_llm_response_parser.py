import unittest

# 'ai.' 접두사를 제거하여 임포트 경로 수정
from llm.llm_response_parser import CotOutputParser

class TestCotOutputParser(unittest.TestCase):

    def setUp(self):
        self.parser = CotOutputParser()

    def test_parse_with_conclusion(self):
        """결론이 포함된 일반적인 응답 파싱 테스트"""
        text = (
            "단계별 추론 과정:\n"
            "1. 사실관계 분석 ...\n"
            "2. 법적 쟁점 ...\n"
            "3. 법원 판단 ...\n\n"
            "결론: 최종 판결 요지입니다."
        )
        expected = {
            "thought_process": "단계별 추론 과정:\n1. 사실관계 분석 ...\n2. 법적 쟁점 ...\n3. 법원 판단 ...",
            "conclusion": "최종 판결 요지입니다."
        }
        self.assertEqual(self.parser.parse(text), expected)

    def test_parse_without_conclusion(self):
        """결론이 없는 응답 파싱 테스트"""
        text = (
            "단계별 추론 과정:\n"
            "1. 사실관계 분석 ...\n"
            "2. 법적 쟁점 ...\n"
            "3. 법원 판단 ..."
        )
        expected = {
            "thought_process": text,
            "conclusion": ""
        }
        self.assertEqual(self.parser.parse(text), expected)

    def test_parse_empty_string(self):
        """빈 문자열 응답 파싱 테스트"""
        text = ""
        expected = {
            "thought_process": "",
            "conclusion": ""
        }
        self.assertEqual(self.parser.parse(text), expected)

    def test_parse_conclusion_only(self):
        """결론만 있는 응답 파싱 테스트"""
        text = "결론: 최종 판결 요지입니다."
        expected = {
            "thought_process": "",
            "conclusion": "최종 판결 요지입니다."
        }
        self.assertEqual(self.parser.parse(text), expected)

if __name__ == '__main__':
    unittest.main()