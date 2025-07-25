import unittest
from unittest.mock import MagicMock
import json
from langchain.llms.base import LLM
from ai.config.tags import SPECIALTY_TAGS

from ai.services.case_analysis_service import CaseAnalysisService

class TestCaseAnalysisService(unittest.TestCase):

    def setUp(self):
        # LLM 인터페이스를 흉내내는 Mock 객체
        self.mock_llm = MagicMock(spec=LLM)
        self.service = CaseAnalysisService(self.mock_llm)
        # 내부 chain을 Mock 으로 교체
        self.service.chain = MagicMock()

    def test_analyze_case_invokes_chain_correctly(self):
        """analyze_case가 chain.invoke에 올바른 파라미터로 호출되는지 검증"""
        expected_output = {
            "issues": ["손해배상 가능 여부"],
            "opinion": "계약 불이행 시 손해배상이 가능합니다."
        }
        self.service.chain.invoke.return_value = {"text": json.dumps({"data": {"report": expected_output}, "tags": ["형사", "사기"]})}

        user_query = "회사 계약 불이행 시 손해배상이 가능한가요?"
        case_docs  = [
            {"id": "2019다1234", "name": "판례1", "text": "내용1"},
            {"id": "2020다5678", "name": "판례2", "text": "내용2"},
        ]
        tag_list_str = ", ".join(SPECIALTY_TAGS)

        result = self.service.analyze_case(user_query, case_docs)

        # JSON 직렬화된 case_docs와 user_query, tag_list가 invoke에 전달되었는지 확인
        self.service.chain.invoke.assert_called_once_with({
            "user_query": user_query,
            "case_docs":  json.dumps(case_docs, ensure_ascii=False),
            "tag_list": tag_list_str,
        })
        # 반환값이 parser로부터 전달된 expected_output과 동일한지 검증
        self.assertEqual(result["case_analysis"].issues, expected_output["issues"])
        self.assertEqual(result["case_analysis"].opinion, expected_output["opinion"])
        self.assertEqual(result["case_analysis"].tags, ["형사", "사기"])

if __name__ == "__main__":
    unittest.main()
