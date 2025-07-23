import os
import json
import glob
from datetime import datetime
from collections import Counter
import re

# Directories
RAW_DIR = '../data/raw'
PROCESSED_DIR = './data/preprocessed'

os.makedirs(PROCESSED_DIR, exist_ok=True)

records = []

# Load and transform only first 10 raw JSON files
filepaths = glob.glob(os.path.join(RAW_DIR, '*.json'))
for filepath in filepaths:
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    # 이하 기존 처리 로직 동일
    case_number = raw.get('사건번호', '').strip()
    case_id = case_number
    title = raw.get('사건명', '').strip()
    decision_date = raw.get('선고일자', '').strip()
    try:
        decision_date_iso = datetime.strptime(decision_date, '%Y-%m-%d').date().isoformat()
    except ValueError:
        decision_date_iso = decision_date

    category = raw.get('사건종류명', '').strip()
    issue = (raw.get('판시사항') or '').replace('【판시사항】', '').strip()
    summary = (raw.get('판결요지') or '').replace('【판결요지】', '').strip()
    full_text = (raw.get('판례내용') or '').replace('【전문】', '').strip()


    # 원본에서 “【참조조문】” 마커 제거
    statutes_raw = (raw.get('참조조문') or '').replace('【참조조문】', '').strip()
    # [1], [2] 같은 번호 단위로 분리
    statute_groups = re.split(r'(?=\[\d+\])', statutes_raw)
    # 각 그룹 내 줄바꿈은 공백으로 바꾸고, 앞뒤 공백 제거
    statutes = [grp.replace('\n', ' ').strip() for grp in statute_groups if grp.strip()]

    # 원본에서 “【참조판례】” 마커 제거
    precedents_raw = (raw.get('참조판례') or '').replace('【참조판례】', '').strip()
    # 마찬가지로 번호 단위로 분리
    precedent_groups = re.split(r'(?=\[\d+\])', precedents_raw)
    precedents = [grp.replace('\n', ' ').strip() for grp in precedent_groups if grp.strip()]

    record = {
        'case_id':       case_id, ## 사건번호
        'title':         title, ## 사건명
        'decision_date': decision_date_iso, ## 선고일자 (ISO 형식)
        'category':      category,  ## 사건종류명
        'issue':         issue, ## 판시사항
        'summary':       summary,   ## 판결요지
        'full_text':     full_text, ## 판례내용
        'statutes':      statutes,  ## 참조조문
        'precedents':    precedents,    ## 참조판례
    }
    records.append(record)

    out_path = os.path.join(PROCESSED_DIR, f"{case_id}.json")
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(record, out_f, ensure_ascii=False, indent=2)


# Compute statistics
total_raw = len(records)
unique_records = {r['case_id']: r for r in records}
total_unique = len(unique_records)

# Date range
dates = []
for rec in unique_records.values():
    try:
        dates.append(datetime.fromisoformat(rec['decision_date']).date())
    except ValueError:
        continue
min_date, max_date = min(dates), max(dates)

# Category distribution
category_counts = Counter(r['category'] for r in unique_records.values())

# Print summary
print("Version: 1.0")
print(f"Date: {datetime.now().date().isoformat()}")
print(f"Total records (raw): {total_raw}")
print(f"Total records (deduplicated): {total_unique}")
print(f"Decision date range: {min_date} ~ {max_date}")
print("Category distribution:")
for cat, count in category_counts.items():
    print(f"  {cat}: {count}")

