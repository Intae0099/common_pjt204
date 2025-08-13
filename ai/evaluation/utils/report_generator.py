"""
RAG 평가 리포트 생성 모듈
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ReportGenerator:
    """RAG 평가 리포트 생성기"""
    
    def __init__(self, reports_dir: str):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_reports(self, 
                        evaluation_results: Dict[str, Any],
                        config: Dict[str, Any]) -> Dict[str, str]:
        """전체 리포트 생성"""
        timestamp = datetime.now()
        
        # 평가 정보 추출
        total_cases = len(evaluation_results.get('case_results', []))
        k_values = config.get('evaluation', {}).get('k_values', [1, 5, 10])
        k_str = '-'.join(map(str, k_values))
        
        # 의미있는 파일명 생성: rag-eval_20cases_k1-5-10_2025-01-13_15-30
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H-%M")
        report_name = f"rag-eval_{total_cases}cases_k{k_str}_{date_str}_{time_str}"
        
        # 하위 폴더 구조 생성: reports/2025-01-13/
        date_folder = self.reports_dir / date_str
        date_folder.mkdir(parents=True, exist_ok=True)
        
        # JSON 리포트 생성
        metrics_file = date_folder / f"{report_name}_metrics.json"
        self._generate_json_report(evaluation_results, config, metrics_file, timestamp)
        
        # 마크다운 요약 리포트 생성
        summary_file = date_folder / f"{report_name}_summary.md"
        self._generate_markdown_report(evaluation_results, config, summary_file, timestamp)
        
        # 최신 리포트 링크 생성 (루트 reports 폴더에)
        try:
            latest_metrics = self.reports_dir / "latest-evaluation_metrics.json"
            latest_summary = self.reports_dir / "latest-evaluation_summary.md"
            
            # 기존 파일이 있으면 삭제
            if latest_metrics.exists():
                latest_metrics.unlink()
            if latest_summary.exists():
                latest_summary.unlink()
            
            # 복사
            import shutil
            shutil.copy2(metrics_file, latest_metrics)
            shutil.copy2(summary_file, latest_summary)
            
        except Exception as e:
            logger.warning(f"최신 리포트 링크 생성 실패: {e}")
        
        return {
            'metrics_file': str(metrics_file),
            'summary_file': str(summary_file)
        }
    
    def _generate_json_report(self, 
                            results: Dict[str, Any], 
                            config: Dict[str, Any],
                            output_file: Path,
                            timestamp: datetime):
        """JSON 형식 상세 리포트 생성"""
        
        report_data = {
            "evaluation_summary": {
                "total_cases": len(results.get('case_results', [])),
                "timestamp": timestamp.isoformat(),
                "config": {
                    "k_values": config.get('evaluation', {}).get('k_values', [1, 3, 5]),
                    "api_endpoint": config.get('api', {}).get('base_url', ''),
                    "timeout_seconds": config.get('api', {}).get('timeout_seconds', 30)
                }
            }
        }
        
        # 메트릭 데이터 추가
        if 'aggregated_metrics' in results:
            aggregated = results['aggregated_metrics']
            
            if 'search_metrics' in aggregated:
                report_data['search_metrics'] = aggregated['search_metrics']
            
            if 'analysis_metrics' in aggregated:
                report_data['analysis_metrics'] = aggregated['analysis_metrics']
        
        # 전체 성능 메트릭 추가
        if 'overall_metrics' in results:
            report_data['overall_metrics'] = results['overall_metrics']
        
        # 케이스별 상세 결과 추가
        if config.get('output', {}).get('include_case_details', True):
            report_data['case_results'] = results.get('case_results', [])
        
        # 에러 정보 추가
        if 'errors' in results:
            report_data['errors'] = results['errors']
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON 리포트 생성 완료: {output_file}")
            
        except Exception as e:
            logger.error(f"JSON 리포트 생성 실패: {e}")
            raise
    
    def _generate_markdown_report(self, 
                                results: Dict[str, Any], 
                                config: Dict[str, Any],
                                output_file: Path,
                                timestamp: datetime):
        """마크다운 형식 요약 리포트 생성"""
        
        md_content = []
        
        # 헤더
        md_content.append("# RAG 성능 평가 결과\n\n")
        md_content.append(f"**평가 일시**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_content.append(f"**총 케이스**: {len(results.get('case_results', []))}개\n")
        
        # 전체 성능 요약
        overall = results.get('overall_metrics', {})
        if overall:
            runtime = overall.get('total_runtime_s', 0)
            md_content.append(f"**평가 소요시간**: {runtime:.1f}초\n\n")
        
        # 핵심 지표 섹션
        md_content.append("## 📊 핵심 지표\n\n")
        
        # 검색 성능
        search_metrics = results.get('aggregated_metrics', {}).get('search_metrics', {})
        if search_metrics:
            md_content.append("### 🔍 검색 성능\n")
            
            recall_1 = search_metrics.get('recall@1', 0) * 100
            recall_5 = search_metrics.get('recall@5', 0) * 100
            recall_10 = search_metrics.get('recall@10', 0) * 100
            precision_1 = search_metrics.get('precision@1', 0) * 100
            mrr = search_metrics.get('mrr', 0)
            
            md_content.append(f"- **Recall@1**: {recall_1:.1f}% (첫 번째 결과에 정답 포함률)\n")
            md_content.append(f"- **Recall@5**: {recall_5:.1f}% (상위 5개 내 정답 포함률)\n")
            md_content.append(f"- **Recall@10**: {recall_10:.1f}% (상위 10개 내 정답 포함률)\n")
            md_content.append(f"- **Precision@1**: {precision_1:.1f}% (첫 번째 결과의 정확도)\n")
            
            # MRR이 0인 경우 처리
            if mrr > 0:
                avg_rank = 1 / mrr
                md_content.append(f"- **MRR**: {mrr:.3f} (평균 {avg_rank:.1f}번째 순위에서 정답 발견)\n\n")
            else:
                md_content.append(f"- **MRR**: {mrr:.3f} (정답을 찾지 못함)\n\n")
        
        # 분석 성능
        analysis_metrics = results.get('aggregated_metrics', {}).get('analysis_metrics', {})
        if analysis_metrics:
            md_content.append("### 🧠 분석 성능\n")
            
            citation_acc = analysis_metrics.get('citation_accuracy', 0) * 100
            sentence_acc = analysis_metrics.get('sentence_prediction_accuracy', 0) * 100
            
            md_content.append(f"- **Citation Accuracy**: {citation_acc:.1f}% (필수 판례 정확 인용률)\n")
            md_content.append(f"- **Sentence Prediction**: {sentence_acc:.1f}% (판결 결과 일치도)\n")
            
            # 선택적 메트릭
            if 'tag_f1' in analysis_metrics:
                tag_f1 = analysis_metrics['tag_f1'] * 100
                md_content.append(f"- **Tag F1-Score**: {tag_f1:.1f}% (법률 분야 태그 분류 정확도)\n")
            
            if 'statute_relevance' in analysis_metrics:
                statute_rel = analysis_metrics['statute_relevance'] * 100
                md_content.append(f"- **Statute Relevance**: {statute_rel:.1f}% (관련 법령 매칭 정확도)\n")
            
            md_content.append("\n")
        
        # 전체 성능
        if overall:
            md_content.append("### ⚡ 전체 성능\n")
            
            e2e_acc = overall.get('end_to_end_accuracy', 0) * 100
            avg_latency = overall.get('average_latency_ms', 0)
            success_rate = overall.get('success_rate', 0) * 100
            
            md_content.append(f"- **End-to-End Accuracy**: {e2e_acc:.1f}% (완전 정답률)\n")
            md_content.append(f"- **평균 응답시간**: {avg_latency:,.1f}ms\n")
            md_content.append(f"- **성공률**: {success_rate:.1f}% (API 호출 성공률)\n\n")
        
        # 개선 권장사항
        md_content.append("## 🎯 개선 권장사항\n\n")
        recommendations = self._generate_recommendations(results)
        for i, rec in enumerate(recommendations, 1):
            md_content.append(f"{i}. {rec}\n")
        
        md_content.append("\n")
        
        # 상세 결과 테이블
        if config.get('output', {}).get('include_case_details', True):
            md_content.append("## 📋 상세 결과\n\n")
            md_content.append(self._generate_results_table(results.get('case_results', [])))
        
        # 에러 정보
        errors = results.get('errors', [])
        if errors:
            md_content.append("\n## ⚠️ 오류 정보\n\n")
            for error in errors:
                md_content.append(f"- **{error.get('case_id', 'Unknown')}**: {error.get('error', 'Unknown error')}\n")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(''.join(md_content))
            
            logger.info(f"마크다운 리포트 생성 완료: {output_file}")
            
        except Exception as e:
            logger.error(f"마크다운 리포트 생성 실패: {e}")
            raise
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        # 검색 성능 기반 권장사항
        search_metrics = results.get('aggregated_metrics', {}).get('search_metrics', {})
        if search_metrics:
            recall_1 = search_metrics.get('recall@1', 0)
            if recall_1 < 0.8:
                recommendations.append(f"검색 정확도 향상 필요 (현재 Recall@1: {recall_1*100:.1f}% → 목표: 80%+)")
        
        # 분석 성능 기반 권장사항
        analysis_metrics = results.get('aggregated_metrics', {}).get('analysis_metrics', {})
        if analysis_metrics:
            citation_acc = analysis_metrics.get('citation_accuracy', 0)
            if citation_acc < 0.85:
                recommendations.append(f"판례 인용 정확도 향상 필요 (현재: {citation_acc*100:.1f}% → 목표: 85%+)")
            
            sentence_acc = analysis_metrics.get('sentence_prediction_accuracy', 0)
            if sentence_acc < 0.8:
                recommendations.append(f"판결 예측 정확도 개선 필요 (현재: {sentence_acc*100:.1f}% → 목표: 80%+)")
        
        # 응답 시간 기반 권장사항
        overall = results.get('overall_metrics', {})
        if overall:
            avg_latency = overall.get('average_latency_ms', 0)
            if avg_latency > 2000:
                recommendations.append(f"응답 시간 최적화 검토 (현재: {avg_latency:.0f}ms → 목표: 2초 이하)")
        
        # 실패 케이스 분석 권장사항
        case_results = results.get('case_results', [])
        failed_cases = [r for r in case_results if not r.get('analysis_success', True)]
        if failed_cases:
            recommendations.append(f"실패 케이스 {len(failed_cases)}개 상세 분석 및 개선 필요")
        
        # 기본 권장사항 (메트릭이 없는 경우)
        if not recommendations:
            recommendations.append("전반적으로 양호한 성능을 보입니다.")
            recommendations.append("지속적인 모니터링을 통한 성능 유지 권장")
        
        return recommendations
    
    def _generate_results_table(self, case_results: List[Dict[str, Any]]) -> str:
        """케이스별 결과 테이블 생성"""
        if not case_results:
            return "결과 데이터가 없습니다.\n"
        
        table = []
        table.append("| 케이스 ID | 검색 성공 | 분석 성공 | 인용 발견 | 판결 일치 | 응답시간(ms) |\n")
        table.append("|---|---|---|---|---|---:|\n")
        
        for result in case_results[:10]:  # 상위 10개만 표시
            case_id = result.get('case_id', 'N/A')
            search_success = "✅" if result.get('search_success', False) else "❌"
            analysis_success = "✅" if result.get('analysis_success', False) else "❌"
            citation_found = "✅" if result.get('citation_found', False) else "❌"
            sentence_match = "✅" if result.get('sentence_match', False) else "❌"
            latency = result.get('latency_ms', 0)
            
            table.append(f"| {case_id} | {search_success} | {analysis_success} | {citation_found} | {sentence_match} | {latency:.0f} |\n")
        
        if len(case_results) > 10:
            table.append(f"\n*총 {len(case_results)}개 케이스 중 상위 10개만 표시*\n")
        
        return ''.join(table)