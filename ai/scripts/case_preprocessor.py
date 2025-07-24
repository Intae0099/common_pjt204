import os
import json
import glob
import re
from datetime import datetime
from collections import Counter
from tqdm import tqdm
from utils.logger import setup_logger, get_logger

# 로거 설정
setup_logger()
logger = get_logger(__name__)

# --------- 설정 ---------
RAW_DATA_DIR     = "F:/S13P11B204/ai/data/raw"
PREPROCESSED_DIR = "F:/S13P11B204/ai/data/preprocessed"
# ------------------------

def parse_date(date_str):
    """
    날짜 문자열을 ISO 포맷으로 변환. 지원 형식: YYYY-MM-DD, YYYY.MM.DD
    실패 시 원본 문자열 반환.
    """
    for fmt in ("%Y-%m-%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(date_str, fmt).date().isoformat()
        except ValueError:
            continue
    return date_str

def get_unique_cases(files):
    """
    파일 목록을 순회하며 JSON을 로드하고,
    사건번호(case_id) 기준으로 중복 제거된 dict 반환.
    """
    cases = {}
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {filepath}: {e}")
            continue

        case_id = raw.get('사건번호', '').strip()
        if not case_id:
            logger.warning(f"No case number in {filepath}")
            continue
        if case_id in cases:
            continue

        title         = raw.get('사건명', '').strip()
        decision_date = parse_date(raw.get('선고일자', '').strip())
        category      = raw.get('사건종류명', '').strip()
        issue         = (raw.get('판시사항')  or '').replace('【판시사항】', '').strip()
        summary       = (raw.get('판결요지')  or '').replace('【판결요지】', '').strip()
        full_text     = (raw.get('판례내용')  or '').replace('【전문】', '').strip()

        # 참조조문 분리
        statutes_raw    = (raw.get('참조조문')  or '').replace('【참조조문】', '').strip()
        statute_groups  = re.split(r'(?=\[\d+\])', statutes_raw)
        statutes        = [g.replace('\n', ' ').strip() for g in statute_groups if g.strip()]

        # 참조판례 분리
        precedents_raw   = (raw.get('참조판례')  or '').replace('【참조판례】', '').strip()
        precedent_groups = re.split(r'(?=\[\d+\])', precedents_raw)
        precedents       = [g.replace('\n', ' ').strip() for g in precedent_groups if g.strip()]

        cases[case_id] = {
            'case_id':       case_id,
            'title':         title,
            'decision_date': decision_date,
            'category':      category,
            'issue':         issue,
            'summary':       summary,
            'full_text':     full_text,
            'statutes':      statutes,
            'precedents':    precedents,
        }
    return cases

def main():
    # 출력 디렉터리 준비
    if not os.path.exists(PREPROCESSED_DIR):
        os.makedirs(PREPROCESSED_DIR)

    # 원본 JSON 파일 모두 검색
    files = glob.glob(os.path.join(RAW_DATA_DIR, '**', '*.json'), recursive=True)
    logger.info(f"Found {len(files)} raw files.")

    # 중복 제거된 사건 데이터 로드
    unique_cases = get_unique_cases(files)
    total_raw    = len(files)
    total_unique = len(unique_cases)

    # 날짜 범위 계산
    dates = []
    for c in unique_cases.values():
        try:
            dates.append(datetime.fromisoformat(c['decision_date']).date())
        except ValueError:
            continue
    if dates:
        min_date, max_date = min(dates), max(dates)
    else:
        min_date = max_date = None

    # 카테고리 분포 집계
    category_counts = Counter(c['category'] for c in unique_cases.values())

    # 통계 로깅
    logger.info("Version: 1.0")
    logger.info(f"Date: {datetime.now().date().isoformat()}")
    logger.info(f"Total records (raw): {total_raw}")
    logger.info(f"Total records (deduplicated): {total_unique}")
    if min_date and max_date:
        logger.info(f"Decision date range: {min_date.isoformat()} ~ {max_date.isoformat()}")
    logger.info("Category distribution:")
    for cat, cnt in category_counts.items():
        logger.info(f"  {cat}: {cnt}")

    # 전처리된 JSON 파일로 저장 (진행 상황 표시)
    for case_id, case_data in tqdm(unique_cases.items(), desc="전처리 진행"):
        out_path = os.path.join(PREPROCESSED_DIR, f"{case_id}.json")
        try:
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Failed to write {out_path}: {e}")

if __name__ == "__main__":
    main()
