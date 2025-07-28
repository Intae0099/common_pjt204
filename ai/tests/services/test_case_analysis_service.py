import unittest
from unittest.mock import MagicMock, patch
import json
from langchain.llms.base import LLM
from config.tags import SPECIALTY_TAGS
from services.case_analysis_service import CaseAnalysisService

class TestCaseAnalysisService(unittest.TestCase):

    def setUp(self):
        # LLM 인터페이스를 흉내내는 Mock 객체
        self.mock_llm = MagicMock(spec=LLM)
        self.service = CaseAnalysisService(self.mock_llm)
        # 내부 chain을 Mock 으로 교체
        self.service.chain = MagicMock()

    @patch('services.case_analysis_service.search_cases')
    def test_analyze_case_invokes_chain_correctly(self, mock_search_cases):
        """analyze_case가 chain.invoke에 올바른 파라미터로 호출되는지 검증"""
        # 1) search_cases가 반환할 원본 문서들
        raw_docs = [
            {"case_id": "2019다1234", "issue": "판례1", "chunk_text": "내용1"},
            {"case_id": "2020다5678", "issue": "판례2", "chunk_text": "내용2"},
        ]
        mock_search_cases.return_value = raw_docs

        # 2) chain.invoke가 리턴할 가짜 LLM 응답
        expected_output = {
            "issues": ["손해배상 가능 여부"],
            "opinion": "계약 불이행 시 손해배상이 가능합니다."
        }
        self.service.chain.invoke.return_value = {
            "text": json.dumps({"data": {"report": expected_output}, "tags": ["형사", "사기"]})
        }

        user_query = "회사 계약 불이행 시 손해배상이 가능한가요?"
        top_k_docs = 2
        tag_list_str = ", ".join(SPECIALTY_TAGS)

        # 3) 실제 호출
        result = self.service.analyze_case(user_query, top_k_docs)

        # 4) formatted_case_docs와 JSON 직렬화
        formatted_docs = [
            {"id": "2019다1234", "issue": "판례1", "text": "내용1"},
            {"id": "2020다5678", "issue": "판례2", "text": "내용2"},
        ]
        expected_docs_json = json.dumps(formatted_docs, ensure_ascii=False)

        # 5) chain.invoke 인자 검증
        self.service.chain.invoke.assert_called_once_with({
            "user_query": user_query,
            "case_docs": expected_docs_json,
            "tag_list": tag_list_str,
        })

        # 6) 반환된 case_analysis 결과 검증
        self.assertEqual(result["case_analysis"].issues, expected_output["issues"])
        self.assertEqual(result["case_analysis"].opinion, expected_output["opinion"])
        self.assertEqual(result["case_analysis"].tags, ["형사", "사기"])

if __name__ == "__main__":
    unittest.main()
