-- 법령 벡터 검색을 위한 테이블 생성
-- pgvector 확장이 이미 활성화되어 있다고 가정

-- 법령 마스터 테이블
CREATE TABLE IF NOT EXISTS legal_statutes (
    dept_code         TEXT,                   -- 소관부처코드
    dept_name         TEXT,                   -- 소관부처명
    statute_id        TEXT PRIMARY KEY,       -- 법령ID
    statute_name      TEXT NOT NULL,          -- 법령명
    promulgation_date TEXT,                   -- 공포일자 (YYYY-MM-DD 또는 YYYY.MM.DD 등)
    promulgation_no   TEXT,                   -- 공포번호
    effective_date    TEXT,                   -- 시행일자
    statute_type_code TEXT,                   -- 법령구분코드
    statute_type_name TEXT,                   -- 법령구분명
    field_code        TEXT,                   -- 법령분야코드
    field_name        TEXT,                   -- 법령분야명
    description       TEXT,                   -- 법령 설명 (생성됨)
    embedding         VECTOR(768),            -- 법령명 + 설명 임베딩
    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW()
);

-- 벡터 검색을 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_legal_statutes_embedding 
ON legal_statutes USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 법령명 기반 텍스트 검색 인덱스
CREATE INDEX IF NOT EXISTS idx_legal_statutes_name 
ON legal_statutes USING gin(to_tsvector('korean', statute_name));

-- 법령 유형별 검색 인덱스
CREATE INDEX IF NOT EXISTS idx_legal_statutes_type 
ON legal_statutes (statute_type_name);

-- 소관부처별 검색 인덱스  
CREATE INDEX IF NOT EXISTS idx_legal_statutes_dept 
ON legal_statutes (dept_name);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_legal_statutes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 생성
CREATE TRIGGER update_legal_statutes_updated_at
    BEFORE UPDATE ON legal_statutes
    FOR EACH ROW
    EXECUTE FUNCTION update_legal_statutes_updated_at();

-- 법령 검증 로그 테이블
CREATE TABLE IF NOT EXISTS statute_validation_logs (
    log_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_text   TEXT NOT NULL,              -- 원본 법령 텍스트
    matched_statute_id TEXT,                    -- 매칭된 법령 ID
    confidence_score FLOAT,                     -- 신뢰도 점수
    validation_result TEXT NOT NULL,            -- 'matched', 'corrected', 'removed', 'suggested'
    suggested_statute_id TEXT,                  -- 제안된 법령 ID (있는 경우)
    error_type      TEXT,                       -- 오류 유형 ('not_found', 'typo', 'outdated' 등)
    session_id      TEXT,                       -- 세션 식별자
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 검증 로그 인덱스
CREATE INDEX IF NOT EXISTS idx_validation_logs_result 
ON statute_validation_logs (validation_result);

CREATE INDEX IF NOT EXISTS idx_validation_logs_session 
ON statute_validation_logs (session_id);

CREATE INDEX IF NOT EXISTS idx_validation_logs_created 
ON statute_validation_logs (created_at);