
import unittest
import psycopg2
import os
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

from modules.search_module import search_cases

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', '.env'))

class TestSearch(unittest.TestCase):
    def setUp(self):
        """테스트 시작 전 DB 연결 및 모델 로드"""
        pass

    def tearDown(self):
        """테스트 종료 후 DB 연결 종료"""
        pass

    def test_metadata_accuracy(self):
        """JSON 파일의 메타데이터가 DB에 정확하게 저장되었는지 검증"""
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"), port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"), user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD")
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

    def test_search_accuracy(self):
        """'신탁' 키워드 검색 시 '2000마2997' 판례가 결과에 포함되는지 검증"""
        query = '신탁'
        results = search_cases(query, top_k=10)
        case_ids = [doc['case_id'] for doc in results]
        self.assertIn('2000마2997', case_ids, f"Case '2000마2997' should be in the search results for '{query}'")

if __name__ == '__main__':
    unittest.main()
