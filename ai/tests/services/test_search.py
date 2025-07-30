
import unittest
import psycopg2
import os
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from unittest.mock import AsyncMock

from services.search_service import SearchService
from llm.models.embedding_model import EmbeddingModel
from llm.models.cross_encoder_model import CrossEncoderModel

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', '.env'))

class TestSearch(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # 실제 모델 클래스나 Mock을 사용해 인스턴스 생성
        self.embedding_model = AsyncMock(spec=EmbeddingModel)
        self.cross_encoder_model = AsyncMock(spec=CrossEncoderModel)
        self.search_service = SearchService(self.embedding_model, self.cross_encoder_model)

        # Mock the get_embedding method
        self.embedding_model.get_embedding.return_value = [0.1] * 768  # Dummy embedding

    async def asyncTearDown(self):
        """테스트 종료 후 DB 연결 종료"""
        pass

    def test_metadata_accuracy(self):
        """JSON 파일의 메타데이터가 DB에 정확하게 저장되었는지 검증"""
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD")
        )
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT title, decision_date, issue, summary FROM legal_cases WHERE case_id = '2000가단13456'")
            result = cur.fetchone()
            self.assertIsNotNone(result, "Case '2000가단13456' not found in the database.")
            
            title, decision_date, issue, summary = result
            self.assertEqual(title, "소유권이전등기등")
            self.assertEqual(str(decision_date), "2001-03-30")
            self.assertEqual(issue, "구 신탁회사의구신탁재산처리에관한법률 및 같은법시행령에 의하여 구성된 구신탁재산처리위원회가 신탁회사의 구신탁재산을 국가에 귀속시키기로 의결한 경우, 구신탁재산이 국유재산으로 귀속되는지 여부(소극)")
            self.assertIn("구 신탁회사의구신탁재산처리에관한법률", summary)
        conn.close()

    async def test_search_accuracy(self):
        """'신탁' 키워드 검색 시 '2000마2997' 판례가 결과에 포함되는지 검증"""
        query = '신탁'
        # Mock the vector_search method to return a predefined result
        self.search_service.vector_search = AsyncMock(return_value=([
            {"case_id": "2000마2997", "title": "신탁 관련 판례", "decision_date": "2000-01-01", "category": "민사", "summary": "신탁 관련 요약", "full_text": "신탁 관련 전문"}
        ], 1))

        results, total_count = await self.search_service.vector_search(
            query,
            page=1,
            size=10
        )
        case_ids = [doc['case_id'] for doc in results]
        self.assertIn('2000마2997', case_ids, f"Case '2000마2997' should be in the search results for '{query}'")
        self.assertEqual(total_count, 1)

if __name__ == '__main__':
    unittest.main()
