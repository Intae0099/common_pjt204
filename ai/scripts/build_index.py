
import os, json, glob
import psycopg2
from psycopg2.extras import execute_batch
from tqdm import tqdm
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from utils.logger import setup_logger, get_logger
from llm.embedding_model import load_model as load_embedding_model

load_dotenv()

setup_logger()
logger = get_logger(__name__)

# --------- 설정 ---------
DATA_DIR      = "F:/S13P11B204/ai/data/preprocessed"
EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
CHUNK_SIZE, CHUNK_OVERLAP = 1800, 200
HNSW_M, HNSW_EF_CONSTRUCTION = 12, 150
# ------------------------

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"), port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"), user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD")
    )
    register_vector(conn)
    return conn

def create_hnsw_index(cur):
    cur.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_legal_chunks_embedding_hnsw
        ON legal_chunks
        USING hnsw (embedding vector_l2_ops)
        WITH (m={HNSW_M}, ef_construction={HNSW_EF_CONSTRUCTION});
    """)

def process_text_to_chunks(case_id, header, body):
    chunks = [{"case_id": case_id, "chunk_index": -1,
               "section": "header", "chunk_text": header}]
    start, idx = 0, 0
    while start < len(body):
        end = start + CHUNK_SIZE
        chunks.append({"case_id": case_id, "chunk_index": idx,
                       "section": "body", "chunk_text": body[start:end]})
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1
    return chunks

def main():
    logger.info("--- 인덱싱 시작 ---")
    conn, cur = get_db_connection(), None
    try:
        cur = conn.cursor()
        model = load_embedding_model()

        files = glob.glob(os.path.join(DATA_DIR, '**', '*.json'), recursive=True)
        logger.info(f"{len(files)}개 파일 처리")

        cases, chunks_all = [], []

        for fp in tqdm(files, desc="JSON 파싱"):
            with open(fp, 'r', encoding='utf-8') as f:
                d = json.load(f)

            cid = d.get("case_id")
            if not cid:
                continue

            raw_cat  = d.get("category") or ""
            category = raw_cat.split('_', 1)[0] if raw_cat else ""

            statutes_txt   = ", ".join(d.get("statutes", [])) or None
            precedents_txt = ", ".join(d.get("precedents", [])) or None

            cases.append((
                cid,
                d.get("title"),
                d.get("decision_date"),
                category,
                d.get("issue"),
                d.get("summary"),
                statutes_txt,
                precedents_txt,
                d.get("full_text")
            ))

            header = (
                f"제목: {d.get('title','')}\n"
                f"쟁점: {d.get('issue','')}\n"
                f"요약: {d.get('summary','')}"
            )
            chunks_all.extend(
                process_text_to_chunks(cid, header, d.get("full_text", ""))
            )

        execute_batch(cur, """
            INSERT INTO legal_cases
              (case_id, title, decision_date, category,
               issue, summary, statutes, precedents, full_text)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (case_id) DO NOTHING
        """, cases)
        conn.commit()
        logger.info("legal_cases 입력 완료")

        texts = [c["chunk_text"] for c in chunks_all]
        logger.info(f"{len(texts)}개 청크 임베딩 생성")
        embeds = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

        chunk_rows = []
        for i, c in enumerate(chunks_all):
            chunk_rows.append((
                c["case_id"], c["chunk_index"], c["section"],
                c["chunk_text"],
                embeds[i].tolist(),
                len(c["chunk_text"].split())
            ))

        execute_batch(cur, """
            INSERT INTO legal_chunks
              (case_id, chunk_index, section,
               chunk_text, embedding, token_count)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (case_id, chunk_index, section) DO NOTHING
        """, chunk_rows)
        conn.commit()
        logger.info("legal_chunks 입력 완료")

        create_hnsw_index(cur)
        conn.commit()
        logger.info("--- 완료 ---")

    finally:
        if cur:  cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    main()

