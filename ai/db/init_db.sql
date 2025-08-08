-- pgvector 확장
CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 모든 메타 + 원문 + 참조를 한 테이블에
CREATE TABLE IF NOT EXISTS legal_cases (
    case_id       TEXT PRIMARY KEY,          -- 필수
    title         TEXT NOT NULL,             -- 필수
    decision_date DATE NOT NULL,             -- 필수
    category      TEXT NOT NULL,             -- 필수 (민사, 형사 …)
    issue         TEXT,                      -- nullable
    summary       TEXT,                      -- nullable
    statutes      TEXT,                      -- 법령 리스트를 쉼표/세미콜론 등으로 직렬화
    precedents    TEXT,                      -- 인용 판례 리스트 직렬화
    full_text     TEXT NOT NULL              -- 필수
);

-- 벡터 청크용 테이블(변경 없음)
CREATE TABLE IF NOT EXISTS legal_chunks (
    chunk_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id      TEXT REFERENCES legal_cases(case_id) ON DELETE CASCADE,
    chunk_index  INT  NOT NULL,
    section      TEXT NOT NULL,
    chunk_text   TEXT NOT NULL,
    embedding    VECTOR(768) NOT NULL,
    token_count  INT,
    UNIQUE (case_id, chunk_index, section)
);
