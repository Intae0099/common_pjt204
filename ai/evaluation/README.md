# RAG 성능 평가 시스템

이 시스템은 법률 AI 플랫폼의 RAG 파이프라인 성능을 평가하기 위한 1단계 MVP입니다.

## 기능

- 검색 성능 메트릭: Recall@K, Precision@K, MRR
- 분석 성능 메트릭: Citation Accuracy, Sentence Prediction
- 자동화된 평가 리포트 생성 (JSON + Markdown)
- 케이스별 상세 결과 추적

## 설치 및 실행

### 1. 의존성 설치

필요한 라이브러리는 이미 프로젝트의 `requirements.txt`에 포함되어 있습니다:

```bash
pip install -r ../requirements.txt
```

추가로 필요한 경우:
```bash
pip install PyYAML
```

### 2. API 서버 실행

평가를 시작하기 전에 법률 AI API 서버가 실행되어야 합니다:

```bash
cd ..
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 평가 실행

```bash
# 전체 평가 (20개 케이스)
python evaluate_rag.py --config config.yaml

# 제한된 케이스로 테스트
python evaluate_rag.py --config config.yaml --max-cases 5

# 도움말
python evaluate_rag.py --help
```

## 설정

`config.yaml` 파일에서 평가 설정을 변경할 수 있습니다:

```yaml
api:
  base_url: "http://localhost:8000"    # API 서버 URL
  timeout_seconds: 30                  # 타임아웃

evaluation:
  k_values: [1, 3, 5]                 # 평가할 K 값들
  enable_analysis: true               # 분석 평가 활성화
  
data:
  eval_file: "../data/eval/total_eval_data.json"  # 평가 데이터

output:
  reports_dir: "evaluation/reports"    # 리포트 출력 디렉터리
  include_case_details: true          # 케이스별 상세 결과 포함
```

## 출력 결과

평가 완료 후 `evaluation/reports/` 디렉터리에 다음 파일들이 생성됩니다:

1. **metrics_YYYYMMDD_HHMMSS.json** - 상세 메트릭 데이터
2. **summary_YYYYMMDD_HHMMSS.md** - 사람이 읽기 쉬운 요약 리포트
3. **latest_metrics.json** - 최신 메트릭 (심볼릭 링크)
4. **latest_summary.md** - 최신 요약 리포트 (심볼릭 링크)

### 예시 출력

```
==================================================
평가 완료!
==================================================
전체 정확도: 70.0%
평균 응답시간: 1500.0ms
성공률: 85.0%
검색 Recall@1: 80.0%
인용 정확도: 75.0%
```

## 테스트

평가 시스템 자체를 테스트하려면:

```bash
python -m pytest tests/test_evaluation.py -v
```

## 구조

```
evaluation/
├── evaluate_rag.py          # 메인 실행 스크립트
├── config.yaml              # 설정 파일
├── utils/
│   ├── data_loader.py       # 평가 데이터 로딩
│   ├── service_caller.py    # API 호출 래퍼
│   ├── metrics.py           # 메트릭 계산
│   └── report_generator.py  # 리포트 생성
├── tests/
│   └── test_evaluation.py   # 테스트 코드
└── reports/                 # 평가 결과 출력
```

## 메트릭 설명

### 검색 메트릭

- **Recall@K**: 상위 K개 결과 중 정답 판례 포함 비율
- **Precision@K**: 상위 K개 결과 중 관련 판례 비율
- **MRR**: 첫 번째 정답의 순위 역수 (Mean Reciprocal Rank)

### 분석 메트릭

- **Citation Accuracy**: 필수 인용 판례의 정확한 인용 비율
- **Sentence Prediction**: 예상 판결 결과 일치도

### 전체 메트릭

- **End-to-End Accuracy**: 전체 파이프라인 정답률
- **Average Latency**: 케이스별 응답 시간 평균
- **Success Rate**: API 호출 성공률

## 문제 해결

### API 연결 오류
```
오류: API 서버에 연결할 수 없습니다.
```
- API 서버가 실행 중인지 확인
- `config.yaml`의 `base_url` 확인
- 방화벽 설정 확인

### 데이터 파일 오류
```
오류: 평가 데이터 파일을 찾을 수 없습니다.
```
- `config.yaml`의 `eval_file` 경로 확인
- `data/eval/total_eval_data.json` 파일 존재 확인

### 의존성 오류
```
ModuleNotFoundError: No module named 'yaml'
```
```bash
pip install PyYAML
```

## 향후 개선사항

- [ ] NDCG@K 메트릭 추가
- [ ] Tag F1-Score 구현
- [ ] Statute Relevance Score 구현
- [ ] 시각화 차트 생성
- [ ] 병렬 처리로 성능 향상
- [ ] 결과 캐싱 기능