# RAG 성능 평가 시스템

법률 AI 플랫폼의 RAG 파이프라인 성능을 자동 평가하는 시스템입니다.

## 🚀 빠른 시작

```bash
# 1. API 서버 실행 (별도 터미널)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. 평가 실행
cd evaluation
python evaluate_rag.py --config config.yaml

# 3. 결과 확인  
cat reports/latest-evaluation_summary.md
```

## 📊 현재 시스템 상태

| 메트릭 | 현재 성능 | 목표 | 상태 |
|-------|-----------|------|------|
| **검색 정확도** | 0.0% | 80%+ | ❌ 심각한 문제 |
| **판례 인용** | 0.0% | 85%+ | ❌ 완전 실패 |
| **판결 예측** | 20.0% | 80%+ | ⚠️ 개선 필요 |
| **응답 시간** | 15.9초 | <2초 | ❌ 최적화 필요 |
| **API 안정성** | 100% | 99%+ | ✅ 정상 |

### 🎯 우선 개선 과제
1. **판례 검색 알고리즘 전면 재검토** (최우선)
2. **응답 시간 최적화** (고우선)
3. **판결 예측 정확도 향상** (중우선)

## 🔧 주요 기능

- **자동화된 평가**: 20케이스를 5분에 완전 자동 평가
- **실시간 모니터링**: RAG 파이프라인 성능 실시간 측정
- **상세 리포트**: 문제점 진단 및 개선 방향 제시
- **의미적 평가**: 법률 용어 유사성 고려한 정교한 평가

## 📋 평가 메트릭

### 검색 성능
- **Recall@K**: 상위 K개에서 정답 발견율
- **Precision@K**: 상위 K개의 정확도  
- **MRR**: 첫 정답 순위의 역수

### 분석 성능  
- **Citation Accuracy**: 필수 판례 인용율
- **Sentence Prediction**: 판결 결과 예측 정확도 (의미적 유사성 평가)
- **Tag F1**: 법률 분야 분류 성능
- **Statute Relevance**: 관련 법령 매칭 정확도

### 전체 성능
- **End-to-End**: 전체 파이프라인 통합 정확도
- **응답 시간**: 평균 API 응답 시간
- **성공률**: API 호출 안정성

## ⚙️ 설정

`config.yaml`에서 평가 환경 설정:
```yaml
api:
  base_url: "http://localhost:8000"  # API 서버 주소
  
evaluation:
  k_values: [1, 3, 5]               # 평가할 K 값
  enable_analysis: true             # 전체 분석 활성화
```

## 📈 출력 결과

평가 완료 후 다음 파일 생성:
- `latest-evaluation_summary.md`: 최신 요약 리포트 (마크다운)
- `latest-evaluation_metrics.json`: 최신 상세 메트릭 (JSON)
- `YYYY-MM-DD/rag-eval_20cases_k1-5-10_YYYY-MM-DD_HH-MM_*`: 날짜별 보관

## 🧪 테스트

```bash
# 단위 테스트 실행
python -m pytest tests/test_evaluation.py -v

# 제한된 케이스로 빠른 테스트
python evaluate_rag.py --config config.yaml --max-cases 3
```

## 🔍 문제 해결

**API 연결 실패**
- API 서버 실행 상태 확인
- `config.yaml` URL 확인

**평가 데이터 오류**  
- `data/eval/total_eval_data.json` 파일 존재 확인

**의존성 오류**
```bash
pip install PyYAML  # 필요시 추가 설치
```