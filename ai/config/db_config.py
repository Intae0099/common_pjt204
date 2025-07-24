import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# db_config.py
# 데이터베이스 설정을 위한 구성 파일

DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "postgres")
