
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.db_config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

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
