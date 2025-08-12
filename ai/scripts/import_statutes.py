#!/usr/bin/env python3
"""
법령검색목록.csv를 파싱하여 legal_statutes 테이블에 임포트하고 벡터화하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import psycopg2
from psycopg2.extras import execute_batch
import logging
from typing import List, Dict, Optional
import os
from pathlib import Path
import time

# 임베딩 모델 임포트
from llm.models.embedding_model import EmbeddingModel
from config.settings import get_database_settings

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class StatuteImporter:
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.db_settings = get_database_settings()
        self.embedding_model = EmbeddingModel()
        
    def connect_db(self):
        """데이터베이스 연결"""
        return psycopg2.connect(
            host=self.db_settings.host,
            port=self.db_settings.port,
            database=self.db_settings.name,
            user=self.db_settings.user,
            password=self.db_settings.password
        )
    
    def parse_csv(self) -> List[Dict]:
        """CSV 파일을 파싱하여 법령 데이터 리스트 반환"""
        statutes = []
        parse_start_time = time.time()
        
        logger.info(f"CSV 파일 파싱 시작: {self.csv_file_path}")
        
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            # 첫 번째 줄(총건수)는 건너뛰기
            next(file)
            
            reader = csv.DictReader(file)
            error_count = 0
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    statute = {
                        'dept_code': row.get('소관부처코드', '').strip(),
                        'dept_name': row.get('소관부처명', '').strip(),
                        'statute_id': row.get('법령ID', '').strip(),
                        'statute_name': row.get('법령명', '').strip(),
                        'promulgation_date': row.get('공포일자', '').strip(),
                        'promulgation_no': row.get('공포번호', '').strip(),
                        'effective_date': row.get('시행일자', '').strip(),
                        'statute_type_code': row.get('법령구분코드', '').strip(),
                        'statute_type_name': row.get('법령구분명', '').strip(),
                        'field_code': row.get('법령분야코드', '').strip(),
                        'field_name': row.get('법령분야명', '').strip()
                    }
                    
                    # 필수 필드 검증
                    if not statute['statute_id'] or not statute['statute_name']:
                        error_count += 1
                        continue
                    
                    # 법령 설명 생성 (법령명 + 법령구분 + 분야)
                    description_parts = [
                        statute['statute_name'],
                        f"({statute['statute_type_name']})" if statute['statute_type_name'] else "",
                        f"[{statute['field_name']}]" if statute['field_name'] else "",
                        f"소관: {statute['dept_name']}" if statute['dept_name'] else ""
                    ]
                    statute['description'] = ' '.join(filter(None, description_parts))
                    
                    statutes.append(statute)
                    
                    # 진행률 표시 (1000개마다)
                    if row_num % 1000 == 0:
                        logger.info(f"파싱 진행률: {len(statutes)}개 처리됨")
                    
                except Exception as e:
                    error_count += 1
                    continue
        
        parse_duration = time.time() - parse_start_time
        logger.info(f"CSV 파싱 완료: {len(statutes)}개 법령, {parse_duration:.1f}초")
        
        return statutes
    
    def generate_embeddings(self, statutes: List[Dict]) -> List[Dict]:
        """법령 데이터에 임베딩 추가"""
        logger.info(f"임베딩 생성 시작: {len(statutes)}개")
        
        # 임베딩을 위한 텍스트 준비 (법령명 + 설명)
        texts = []
        for statute in statutes:
            embedding_text = f"{statute['statute_name']} {statute['description']}"
            texts.append(embedding_text)
        
        # 배치로 임베딩 생성 (성능 최적화)
        batch_size = 50
        embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for batch_idx, i in enumerate(range(0, len(texts), batch_size), 1):
            batch_texts = texts[i:i + batch_size]
            
            try:
                # 배치 처리를 위해 SentenceTransformer의 encode 메서드 직접 사용
                batch_embeddings = self.embedding_model._model.encode(batch_texts, convert_to_numpy=True)
                embeddings.extend([embedding.tolist() for embedding in batch_embeddings])
                
                if batch_idx % 10 == 0:  # 10배치마다 로그
                    processed = min(i + batch_size, len(texts))
                    progress_percent = (processed / len(texts)) * 100
                    logger.info(f"임베딩 진행률: {progress_percent:.0f}% ({processed}/{len(texts)})")
                
            except Exception as e:
                logger.error(f"배치 {batch_idx} 임베딩 실패: {e}")
                dummy_embeddings = [[0.0] * 768 for _ in batch_texts]
                embeddings.extend(dummy_embeddings)
        
        # 임베딩을 법령 데이터에 추가
        for statute, embedding in zip(statutes, embeddings):
            statute['embedding'] = embedding
        
        logger.info(f"임베딩 생성 완료: {len(statutes)}개")
        
        return statutes
    
    def insert_statutes(self, statutes: List[Dict]):
        """법령 데이터를 데이터베이스에 삽입"""
        logger.info(f"데이터베이스 삽입 시작: {len(statutes)}개")
        
        conn = self.connect_db()
        try:
            with conn.cursor() as cur:
                # 기존 데이터 삭제
                cur.execute("TRUNCATE TABLE legal_statutes")
                
                # 삽입할 데이터 준비
                insert_data = []
                for statute in statutes:
                    insert_data.append((
                        statute['dept_code'],
                        statute['dept_name'], 
                        statute['statute_id'],
                        statute['statute_name'],
                        statute['promulgation_date'],
                        statute['promulgation_no'],
                        statute['effective_date'],
                        statute['statute_type_code'],
                        statute['statute_type_name'],
                        statute['field_code'],
                        statute['field_name'],
                        statute['description'],
                        statute['embedding']
                    ))
                
                # 배치 삽입
                execute_batch(cur, """
                    INSERT INTO legal_statutes 
                    (dept_code, dept_name, statute_id, statute_name, promulgation_date,
                     promulgation_no, effective_date, statute_type_code, statute_type_name,
                     field_code, field_name, description, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, insert_data, page_size=100)
                
                conn.commit()
                
                # 결과 확인
                cur.execute("SELECT COUNT(*) FROM legal_statutes")
                total_count = cur.fetchone()[0]
                logger.info(f"데이터베이스 삽입 완료: {total_count}개")
                    
        except Exception as e:
            conn.rollback()
            logger.error(f"데이터베이스 삽입 오류: {e}")
            raise
        finally:
            conn.close()
    
    def run(self):
        """전체 임포트 프로세스 실행"""
        logger.info("법령 임포트 프로세스 시작")
        
        try:
            # 1. CSV 파싱
            statutes = self.parse_csv()
            if not statutes:
                logger.error("파싱된 법령 데이터가 없습니다.")
                return
            
            # 2. 임베딩 생성
            statutes_with_embeddings = self.generate_embeddings(statutes)
            
            # 3. 데이터베이스 삽입
            self.insert_statutes(statutes_with_embeddings)
            
            logger.info(f"법령 임포트 완료: {len(statutes_with_embeddings)}개")
            
        except Exception as e:
            logger.error(f"임포트 프로세스 오류: {e}")
            raise

def main():
    """메인 함수"""
    # CSV 파일 경로
    csv_file_path = Path(__file__).parent.parent / "data" / "법령검색목록.csv"
    
    if not csv_file_path.exists():
        logger.error(f"CSV 파일을 찾을 수 없습니다: {csv_file_path}")
        return
    
    # 임포터 실행
    importer = StatuteImporter(str(csv_file_path))
    importer.run()

if __name__ == "__main__":
    main()