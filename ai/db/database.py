from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# dockerfile_postgreSql 에서 확인된 정보로 데이터베이스 URL 생성
# 형식: "postgresql://사용자이름:비밀번호@호스트:포트/데이터베이스이름"
from config.db_config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 데이터베이스 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 데이터베이스 세션을 생성하기 위한 SessionLocal 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 모델을 만들기 위한 기본 클래스
Base = declarative_base()

# 데이터베이스 세션을 반환하는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print(SQLALCHEMY_DATABASE_URL)  # 데이터베이스 URL 출력
    print("Database engine created successfully.")
    # 데이터베이스 연결 테스트
    try:
        with engine.connect() as connection:
            print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")
    # 세션 생성 테스트
    try:
        db = SessionLocal()
        print("Session created successfully.")
        db.close()
    except Exception as e:
        print(f"Session creation failed: {e}")
    print("Database setup complete.")