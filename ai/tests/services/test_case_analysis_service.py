import json
import unittest
from unittest.mock import patch, MagicMock

from services.case_analysis_service import CaseAnalysisService
from app.api.schemas.analysis import CaseAnalysisResult
from llm.clients.langchain_client import Gpt4oMini
from config.tags import SPECIALTY_TAGS

class TestCaseAnalysisService(unittest.TestCase):
    def setUp(self):
        # 1) LLM도 가짜로
        llm = MagicMock(spec=Gpt4oMini)
        self.service = CaseAnalysisService(llm)
        # 2) chain 전체를 MagicMock으로 교체
        self.service.chain = MagicMock()
        
    @patch('services.case_analysis_service.search_cases')
    def test_analyze_case_invokes_chain_correctly(self, mock_search_cases):
        """analyze_case가 chain.invoke에 올바른 파라미터로 호출되고, 반환값이 제대로 파싱되는지 검증"""
        # 1) search_cases 리턴 설정
        raw_docs = [
            {"case_id": "2019다1234", "issue": "판례1", "chunk_text": "내용1"},
            {"case_id": "2020다5678", "issue": "판례2", "chunk_text": "내용2"},
        ]
        mock_search_cases.return_value = raw_docs

        # 2) 체인 invoke가 리턴할 페이로드 구성
        payload = {
            "data": {
                "report": {
                    "issues": ["손해배상 가능 여부"],
                    "opinion": "계약 불이행 시 손해배상이 가능합니다.",
                    "sentencePrediction": "징역 6개월",
                    "confidence": 0.85,
                    "references": {"cases": [], "statutes": []}
                }
            },
            "tags": ["형사", "사기"],
            "recommendedLawyers": [
                {"id": 1, "name": "김변호사", "matchScore": 0.9}
            ]
        }
        # ★ JSON 분기를 타도록, 유효한 JSON 문자열 생성
        json_str = json.dumps(payload, ensure_ascii=False)
        raw_json = "{\n" + json_str[1:]
        self.service.chain.invoke.return_value = {"text": raw_json}

        user_query = "회사 계약 불이행 시 손해배상이 가능한가요?"
        top_k_docs = 2
        tag_list_str = ", ".join(SPECIALTY_TAGS)

        # 3) 실제 호출
        result = self.service.analyze_case(user_query, top_k_docs)

        # 4) formatted_docs JSON 문자열화
        formatted_docs = [
            {"id": "2019다1234", "issue": "판례1", "text": "내용1"},
            {"id": "2020다5678", "issue": "판례2", "text": "내용2"},
        ]
        expected_docs_json = json.dumps(formatted_docs, ensure_ascii=False)

        # 5) chain.invoke 호출 인자 검증
        self.service.chain.invoke.assert_called_once_with({
            "user_query": user_query,
            "case_docs": expected_docs_json,
            "tag_list": tag_list_str,
        })

        # 6) 반환된 case_analysis 결과 검증
        case_analysis: CaseAnalysisResult = result["case_analysis"]
        self.assertEqual(case_analysis.issues, payload["data"]["report"]["issues"])
        self.assertEqual(case_analysis.opinion, payload["data"]["report"]["opinion"])
        self.assertEqual(
            case_analysis.expected_sentence,
            payload["data"]["report"]["sentencePrediction"]
        )
        self.assertEqual(
            case_analysis.confidence,
            payload["data"]["report"]["confidence"]
        )
        self.assertEqual(
            case_analysis.references,
            payload["data"]["report"]["references"]
        )
        self.assertEqual(case_analysis.tags, payload["tags"])
        self.assertEqual(case_analysis.recommendedLawyers, payload["recommendedLawyers"])