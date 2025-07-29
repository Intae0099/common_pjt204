import unittest

# 실제 코드가 있는 경로로 수정
from llm.llm_response_parser import CotOutputParser, parse_case_analysis_output, CaseAnalysisResult

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


class TestCaseAnalysisParser(unittest.TestCase):

    def test_parse_full_output(self):
        raw_text = """
            쟁점:
            1. 첫 번째 쟁점입니다.
            2. 두 번째 쟁점입니다.

            소견: 이 사건에 대한 저의 소견입니다.

            예상 형량: 징역 2년, 집행유예 3년

            신뢰도: 0.95
        """
        result = parse_case_analysis_output(raw_text)
        self.assertIsInstance(result, CaseAnalysisResult)
        self.assertEqual(result.issues, ["첫 번째 쟁점입니다.", "두 번째 쟁점입니다."])
        self.assertEqual(result.opinion, "이 사건에 대한 저의 소견입니다.")
        self.assertEqual(result.expected_sentence, "징역 2년, 집행유예 3년")
        self.assertEqual(result.confidence, 0.95)

    def test_parse_missing_fields(self):
        raw_text = """
            쟁점:
            1. 쟁점만 있습니다.

            소견: 소견만 있습니다.
        """
        result = parse_case_analysis_output(raw_text)
        self.assertIsInstance(result, CaseAnalysisResult)
        self.assertEqual(result.issues, ["쟁점만 있습니다."])
        self.assertEqual(result.opinion, "소견만 있습니다.")
        self.assertEqual(result.expected_sentence, "")  # 기본값
        self.assertEqual(result.confidence, 0.0)        # 기본값

    def test_parse_invalid_confidence(self):
        raw_text = """
            신뢰도: abc
        """
        result = parse_case_analysis_output(raw_text)
        self.assertIsInstance(result, CaseAnalysisResult)
        self.assertEqual(result.confidence, 0.0)

    def test_parse_empty_string(self):
        raw_text = ""
        result = parse_case_analysis_output(raw_text)
        self.assertIsInstance(result, CaseAnalysisResult)
        self.assertEqual(result.issues, [])
        self.assertEqual(result.opinion, "")
        self.assertEqual(result.expected_sentence, "")
        self.assertEqual(result.confidence, 0.0)

    def test_parse_issues_bullet_points(self):
        raw_text = """
            쟁점:
            - 첫 번째 쟁점
            * 두 번째 쟁점

            소견: (없음)
        """
        result = parse_case_analysis_output(raw_text)
        self.assertIsInstance(result, CaseAnalysisResult)
        self.assertEqual(result.issues, ["첫 번째 쟁점", "두 번째 쟁점"])

    def test_parse_issues_no_prefix(self):
        raw_text = """
            쟁점:
            첫 번째 쟁점
            두 번째 쟁점

            소견: (없음)
        """
        result = parse_case_analysis_output(raw_text)
        self.assertIsInstance(result, CaseAnalysisResult)
        self.assertEqual(result.issues, ["첫 번째 쟁점", "두 번째 쟁점"])



if __name__ == '__main__':
    unittest.main()
