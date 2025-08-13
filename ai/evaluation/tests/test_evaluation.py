"""
RAG 평가 시스템 기본 테스트
"""
import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# 테스트를 위한 경로 설정
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import EvalDataLoader
from utils.metrics import MetricsCalculator
from utils.service_caller import ServiceCaller
from utils.report_generator import ReportGenerator

class TestEvalDataLoader(unittest.TestCase):
    """데이터 로더 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.test_data = [
            {
                "id": "test_001",
                "category": "형사",
                "query_case": {
                    "title": "테스트 사건",
                    "summary": "테스트 요약",
                    "fullText": "테스트 전문 내용입니다."
                },
                "gold": {
                    "must_cite_cases": ["2021고합456"],
                    "expected_sentence": "무죄",
                    "support_snippets": [],
                    "tags": ["폭력·폭행"],
                    "statutes": [
                        {
                            "name": "형법",
                            "article": "제20조",
                            "description": "정당행위"
                        }
                    ]
                }
            }
        ]
        
        # 임시 파일 생성
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        )
        json.dump(self.test_data, self.temp_file, ensure_ascii=False)
        self.temp_file.close()
        
        self.data_loader = EvalDataLoader(self.temp_file.name)
    
    def tearDown(self):
        """테스트 정리"""
        os.unlink(self.temp_file.name)
    
    def test_load_eval_data(self):
        """평가 데이터 로딩 테스트"""
        data = self.data_loader.load_eval_data()
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 'test_001')
        self.assertIn('query_case', data[0])
        self.assertIn('gold', data[0])
    
    def test_validate_data_structure(self):
        """데이터 구조 검증 테스트"""
        data = self.data_loader.load_eval_data()
        
        # 필수 필드 확인
        case = data[0]
        self.assertIn('id', case)
        self.assertIn('query_case', case)
        self.assertIn('gold', case)
        
        # query_case 필드 확인
        query_case = case['query_case']
        self.assertIn('title', query_case)
        self.assertIn('summary', query_case)
        self.assertIn('fullText', query_case)
        
        # gold 필드 확인
        gold = case['gold']
        self.assertIn('must_cite_cases', gold)
        self.assertIn('expected_sentence', gold)
        self.assertIsInstance(gold['must_cite_cases'], list)
    
    def test_get_statistics(self):
        """통계 정보 테스트"""
        data = self.data_loader.load_eval_data()
        stats = self.data_loader.get_statistics(data)
        
        self.assertEqual(stats['total_cases'], 1)
        self.assertIn('categories', stats)
        self.assertEqual(stats['categories']['형사'], 1)


class TestMetricsCalculator(unittest.TestCase):
    """메트릭 계산기 테스트"""
    
    def setUp(self):
        self.calculator = MetricsCalculator(k_values=[1, 3, 5])
    
    def test_calculate_search_metrics(self):
        """검색 메트릭 계산 테스트"""
        gold_cases = ["2021고합456", "2022고합123"]
        retrieved_results = [
            {"case_id": "2021고합456", "rank": 1},
            {"case_id": "2023고합789", "rank": 2},
            {"case_id": "2022고합123", "rank": 3}
        ]
        
        metrics = self.calculator.calculate_search_metrics(gold_cases, retrieved_results)
        
        # Recall@1 = 1/2 = 0.5 (첫 번째에 정답 1개)
        self.assertEqual(metrics['recall@1'], 0.5)
        
        # Recall@3 = 2/2 = 1.0 (상위 3개에 정답 2개 모두)
        self.assertEqual(metrics['recall@3'], 1.0)
        
        # Precision@1 = 1/1 = 1.0
        self.assertEqual(metrics['precision@1'], 1.0)
        
        # MRR = 1/1 = 1.0 (첫 번째 순위에 정답)
        self.assertEqual(metrics['mrr'], 1.0)
    
    def test_calculate_citation_accuracy(self):
        """인용 정확도 계산 테스트"""
        gold_data = {
            "must_cite_cases": ["2021고합456"]
        }
        
        prediction = {
            "references": {
                "cases": [{"case_id": "2021고합456"}]
            },
            "opinion": "본 판례에서는 2021고합456 사건을 참조하여..."
        }
        
        metrics = self.calculator.calculate_analysis_metrics(gold_data, prediction)
        
        # 정확히 인용했으므로 1.0
        self.assertEqual(metrics['citation_accuracy'], 1.0)
    
    def test_calculate_sentence_accuracy(self):
        """판결 문장 정확도 테스트"""
        gold_data = {
            "must_cite_cases": [],
            "expected_sentence": "무죄"
        }
        
        prediction = {
            "expected_sentence": "무죄 판결이 예상됩니다"
        }
        
        metrics = self.calculator.calculate_analysis_metrics(gold_data, prediction)
        
        # 금본 판결이 예측에 포함되어 있으므로 1.0
        self.assertEqual(metrics['sentence_prediction_accuracy'], 1.0)


class TestServiceCaller(unittest.TestCase):
    """서비스 호출자 테스트"""
    
    def setUp(self):
        self.service_caller = ServiceCaller("http://localhost:8000")
    
    def test_extract_search_results(self):
        """검색 결과 추출 테스트"""
        mock_response = {
            "success": True,
            "data": {
                "items": [
                    {
                        "caseId": "2021고합456",
                        "title": "테스트 판례",
                        "category": "형사",
                        "summary": "테스트 요약"
                    }
                ]
            }
        }
        
        results = self.service_caller.extract_search_results(mock_response)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['case_id'], "2021고합456")
        self.assertEqual(results[0]['rank'], 1)
    
    def test_extract_analysis_result(self):
        """분석 결과 추출 테스트"""
        mock_response = {
            "success": True,
            "data": {
                "report": {
                    "issues": ["주요 쟁점"],
                    "opinion": "법적 의견",
                    "expected_sentence": "무죄",
                    "confidence": 0.85
                }
            }
        }
        
        result = self.service_caller.extract_analysis_result(mock_response)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['expected_sentence'], "무죄")
        self.assertEqual(result['confidence'], 0.85)


class TestReportGenerator(unittest.TestCase):
    """리포트 생성기 테스트"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.report_generator = ReportGenerator(self.temp_dir)
    
    def tearDown(self):
        """테스트 정리"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_generate_reports(self):
        """리포트 생성 테스트"""
        test_results = {
            "aggregated_metrics": {
                "search_metrics": {
                    "recall@1": 0.8,
                    "precision@1": 0.9,
                    "mrr": 0.85
                },
                "analysis_metrics": {
                    "citation_accuracy": 0.75,
                    "sentence_prediction_accuracy": 0.8
                }
            },
            "overall_metrics": {
                "end_to_end_accuracy": 0.7,
                "average_latency_ms": 1500,
                "total_runtime_s": 30
            },
            "case_results": [
                {
                    "case_id": "test_001",
                    "search_success": True,
                    "analysis_success": True,
                    "citation_found": True,
                    "sentence_match": True,
                    "latency_ms": 1200
                }
            ],
            "errors": []
        }
        
        test_config = {
            "evaluation": {"k_values": [1, 3, 5]},
            "api": {"base_url": "http://localhost:8000", "timeout_seconds": 30},
            "output": {"include_case_details": True}
        }
        
        report_files = self.report_generator.generate_reports(test_results, test_config)
        
        # 파일 생성 확인
        self.assertIn('metrics_file', report_files)
        self.assertIn('summary_file', report_files)
        
        metrics_file = Path(report_files['metrics_file'])
        summary_file = Path(report_files['summary_file'])
        
        self.assertTrue(metrics_file.exists())
        self.assertTrue(summary_file.exists())
        
        # JSON 파일 내용 확인
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        
        self.assertIn('evaluation_summary', metrics_data)
        self.assertIn('search_metrics', metrics_data)
        self.assertIn('analysis_metrics', metrics_data)


class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def test_end_to_end_flow(self):
        """전체 플로우 테스트 (모의 데이터 사용)"""
        # 1. 테스트 데이터 준비
        test_data = [
            {
                "id": "integration_test",
                "category": "형사",
                "query_case": {
                    "title": "통합 테스트 사건",
                    "summary": "통합 테스트",
                    "fullText": "통합 테스트용 사건 내용"
                },
                "gold": {
                    "must_cite_cases": ["2021고합456"],
                    "expected_sentence": "무죄"
                }
            }
        ]
        
        # 2. 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_file = f.name
        
        try:
            # 3. 데이터 로더 테스트
            data_loader = EvalDataLoader(temp_file)
            eval_data = data_loader.load_eval_data()
            self.assertEqual(len(eval_data), 1)
            
            # 4. 메트릭 계산기 테스트
            calculator = MetricsCalculator()
            
            # 모의 검색 결과
            mock_search_results = [{"case_id": "2021고합456", "rank": 1}]
            search_metrics = calculator.calculate_search_metrics(
                gold_cases=["2021고합456"],
                retrieved_results=mock_search_results
            )
            self.assertEqual(search_metrics['recall@1'], 1.0)
            
            # 모의 분석 결과
            mock_analysis = {
                "references": {"cases": [{"case_id": "2021고합456"}]},
                "expected_sentence": "무죄 판결"
            }
            analysis_metrics = calculator.calculate_analysis_metrics(
                gold_data=eval_data[0]['gold'],
                prediction=mock_analysis
            )
            self.assertEqual(analysis_metrics['citation_accuracy'], 1.0)
            
            print("통합 테스트 통과!")
            
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)