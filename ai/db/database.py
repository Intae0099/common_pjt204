
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from utils.logger import setup_logger, get_logger

load_dotenv() # Load environment variables from .env file

setup_logger()
logger = get_logger(__name__)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_psycopg2_connection():
    """
    Returns a raw psycopg2 connection.
    """
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

if __name__ == "__main__":
    logger.debug(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
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
