
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Generator

from config.settings import get_database_settings
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

# 데이터베이스 설정 가져오기
db_settings = get_database_settings()

# SQLAlchemy 설정
engine = create_engine(db_settings.url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    """SQLAlchemy 세션을 반환하는 의존성 주입 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_psycopg2_connection():
    """
    Returns a raw psycopg2 connection.
    """
    return psycopg2.connect(**db_settings.psycopg2_params)

if __name__ == "__main__":
    logger.debug(f"Database URL: {db_settings.url}")
    logger.info("Database engine created successfully.")
    try:
        with engine.connect() as connection:
            logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    try:
        db = SessionLocal()
        logger.info("Session created successfully.")
        db.close()
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
    logger.info("Database setup complete.")
