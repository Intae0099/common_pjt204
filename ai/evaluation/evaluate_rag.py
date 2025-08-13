#!/usr/bin/env python3
"""
RAG 성능 평가 메인 실행 스크립트

사용법:
    python evaluate_rag.py --config config.yaml
    python evaluate_rag.py --config config.yaml --max-cases 5
"""

import argparse
import asyncio
import logging
import time
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List

# 현재 디렉터리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import EvalDataLoader
from utils.service_caller import ServiceCaller
from utils.metrics import MetricsCalculator
from utils.report_generator import ReportGenerator

class EvaluationRunner:
    """RAG 평가 실행기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.setup_logging()
        
        # 컴포넌트 초기화
        self.data_loader = EvalDataLoader(config['data']['eval_file'])
        self.service_caller = ServiceCaller(
            base_url=config['api']['base_url'],
            timeout=config['api']['timeout_seconds']
        )
        self.metrics_calculator = MetricsCalculator(
            k_values=config['evaluation']['k_values']
        )
        self.report_generator = ReportGenerator(
            reports_dir=config['output']['reports_dir']
        )
        
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """로깅 설정"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        
        # 로그 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 파일 핸들러
        log_file = log_config.get('file')
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
        
        # 루트 로거 설정
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)
        if log_file:
            root_logger.addHandler(file_handler)
    
    async def run_evaluation(self, max_cases: int = None) -> Dict[str, Any]:
        """전체 평가 실행"""
        start_time = time.time()
        
        self.logger.info("RAG 성능 평가 시작")
        
        try:
            # 1. 데이터 로딩 및 검증
            self.logger.info("평가 데이터 로딩 중...")
            eval_data = self.data_loader.load_eval_data()
            
            if max_cases:
                eval_data = eval_data[:max_cases]
                self.logger.info(f"평가 케이스 제한: {max_cases}개")
            
            data_stats = self.data_loader.get_statistics(eval_data)
            self.logger.info(f"평가 데이터 통계: {data_stats}")
            
            # 2. API 서버 상태 확인
            self.logger.info("API 서버 연결 확인 중...")
            if not self.service_caller.health_check():
                raise RuntimeError("API 서버에 연결할 수 없습니다.")
            
            # 3. 케이스별 평가 실행
            self.logger.info(f"{len(eval_data)}개 케이스 평가 시작...")
            case_results = []
            all_case_metrics = []
            errors = []
            
            for i, case in enumerate(eval_data):
                self.logger.info(f"케이스 {i+1}/{len(eval_data)} 평가 중: {case['id']}")
                
                try:
                    case_result, case_metrics = await self.evaluate_single_case(case)
                    case_results.append(case_result)
                    all_case_metrics.append(case_metrics)
                    
                except Exception as e:
                    self.logger.error(f"케이스 {case['id']} 평가 실패: {e}")
                    errors.append({
                        'case_id': case['id'],
                        'error': str(e)
                    })
                    # 실패한 케이스도 결과에 포함
                    case_results.append({
                        'case_id': case['id'],
                        'search_success': False,
                        'analysis_success': False,
                        'citation_found': False,
                        'sentence_match': False,
                        'latency_ms': 0,
                        'error': str(e)
                    })
            
            # 4. 메트릭 집계
            self.logger.info("메트릭 집계 중...")
            aggregated_metrics = self.metrics_calculator.aggregate_metrics(all_case_metrics)
            
            # 5. 전체 성능 메트릭 계산
            total_runtime = time.time() - start_time
            overall_metrics = self.metrics_calculator.calculate_overall_metrics(
                case_results, total_runtime
            )
            
            # 6. 결과 정리
            evaluation_results = {
                'aggregated_metrics': aggregated_metrics,
                'overall_metrics': overall_metrics,
                'case_results': case_results,
                'errors': errors,
                'data_statistics': data_stats
            }
            
            # 7. 리포트 생성
            self.logger.info("리포트 생성 중...")
            report_files = self.report_generator.generate_reports(
                evaluation_results, self.config
            )
            
            self.logger.info(f"평가 완료 - 소요시간: {total_runtime:.1f}초")
            self.logger.info(f"리포트 파일: {report_files}")
            
            return evaluation_results
            
        except Exception as e:
            self.logger.error(f"평가 실행 중 오류 발생: {e}")
            raise
    
    async def evaluate_single_case(self, case: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Dict[str, float]]]:
        """단일 케이스 평가"""
        case_id = case['id']
        query_case = case['query_case']
        gold_data = case['gold']
        
        start_time = time.time()
        
        try:
            # 1. 검색 평가 (순수 검색 성능)
            search_results = []
            search_success = False
            search_metrics = {}
            
            if self.config['evaluation']['enable_search']:
                try:
                    # 별도 검색 API 호출
                    search_query = query_case.get('fullText', '') or query_case.get('summary', '')
                    search_response = self.service_caller.search_cases(
                        query=search_query, 
                        size=self.config['evaluation']['search_top_k']
                    )
                    search_results = self.service_caller.extract_search_results(search_response)
                    search_success = len(search_results) > 0
                    
                    # 검색 메트릭 계산
                    search_metrics = self.metrics_calculator.calculate_search_metrics(
                        gold_cases=gold_data['must_cite_cases'],
                        retrieved_results=search_results
                    )
                except Exception as e:
                    self.logger.error(f"검색 평가 오류: {e}")
                    search_metrics = self.metrics_calculator._empty_search_metrics()
            else:
                search_metrics = self.metrics_calculator._empty_search_metrics()
            
            # 2. 분석 평가 (전체 RAG 파이프라인)
            analysis_response = self.service_caller.analyze_case(query_case)
            analysis_result = self.service_caller.extract_analysis_result(analysis_response)
            analysis_success = analysis_result is not None
            
            # 2. 분석 메트릭 계산
            analysis_metrics = {}
            if analysis_result and self.config['evaluation']['enable_analysis']:
                analysis_metrics = self.metrics_calculator.calculate_analysis_metrics(
                    gold_data=gold_data,
                    prediction=analysis_result
                )
            
            # 3. 케이스 결과 정리
            latency_ms = (time.time() - start_time) * 1000
            
            # 주요 성공 지표 계산
            citation_found = False
            if analysis_result:
                cited_cases = self.service_caller.extract_cited_cases(analysis_result)
                gold_citations = set(gold_data['must_cite_cases'])
                cited_set = set(cited_cases)
                citation_found = len(gold_citations & cited_set) > 0
            
            sentence_match = False
            if analysis_result:
                pred_sentence = analysis_result.get('expected_sentence', '').lower()
                gold_sentence = gold_data.get('expected_sentence', '').lower()
                sentence_match = gold_sentence in pred_sentence if gold_sentence else False
            
            case_result = {
                'case_id': case_id,
                'search_success': search_success,
                'analysis_success': analysis_success,
                'citation_found': citation_found,
                'sentence_match': sentence_match,
                'latency_ms': latency_ms,
                'search_results_count': len(search_results)
            }
            
            case_metrics = {
                'search_metrics': search_metrics,
                'analysis_metrics': analysis_metrics
            }
            
            return case_result, case_metrics
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.logger.error(f"케이스 {case_id} 평가 중 오류: {e}")
            
            case_result = {
                'case_id': case_id,
                'search_success': False,
                'analysis_success': False,
                'citation_found': False,
                'sentence_match': False,
                'latency_ms': latency_ms,
                'error': str(e)
            }
            
            case_metrics = {
                'search_metrics': self.metrics_calculator._empty_search_metrics(),
                'analysis_metrics': {}
            }
            
            return case_result, case_metrics

def load_config(config_file: str) -> Dict[str, Any]:
    """설정 파일 로딩"""
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_file}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="RAG 성능 평가 도구")
    parser.add_argument("--config", "-c", required=True, help="설정 파일 경로")
    parser.add_argument("--max-cases", "-m", type=int, help="최대 평가 케이스 수 (테스트용)")
    
    args = parser.parse_args()
    
    try:
        # 설정 로딩
        config = load_config(args.config)
        
        # 평가 실행
        runner = EvaluationRunner(config)
        results = await runner.run_evaluation(max_cases=args.max_cases)
        
        print("\\n" + "="*50)
        print("평가 완료!")
        print("="*50)
        
        # 주요 결과 출력
        overall = results.get('overall_metrics', {})
        if overall:
            print(f"전체 정확도: {overall.get('end_to_end_accuracy', 0)*100:.1f}%")
            print(f"평균 응답시간: {overall.get('average_latency_ms', 0):.1f}ms")
            print(f"성공률: {overall.get('success_rate', 0)*100:.1f}%")
        
        aggregated = results.get('aggregated_metrics', {})
        search_metrics = aggregated.get('search_metrics', {})
        if search_metrics:
            print(f"검색 Recall@1: {search_metrics.get('recall@1', 0)*100:.1f}%")
        
        analysis_metrics = aggregated.get('analysis_metrics', {})
        if analysis_metrics:
            print(f"인용 정확도: {analysis_metrics.get('citation_accuracy', 0)*100:.1f}%")
        
        errors = results.get('errors', [])
        if errors:
            print(f"\\n오류 발생: {len(errors)}개 케이스")
        
    except Exception as e:
        print(f"평가 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())