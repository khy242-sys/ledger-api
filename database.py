import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()   # .env 파일을 읽어서 환경변수로 등록한다
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ledger.db")   # 못 읽으면 SQLite를 쓴다

kwargs = {"echo": True}   # 실행되는 SQL을 터미널에 보여 준다(공부할 때 유용하다)
if DATABASE_URL.startswith("sqlite"):
    kwargs["connect_args"] = {"check_same_thread": False}   # SQLite에서만 필요한 옵션

# Engine: DB로 가는 연결을 관리한다. 앱에 하나만 만든다.
engine = create_engine(DATABASE_URL, **kwargs)

# Session 공장: 요청마다 여기서 세션을 하나씩 찍어 낸다.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base: 모든 테이블 클래스의 공통 부모
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()   # 이 요청 전용 세션을 연다
    try:
        yield db          # 요청을 처리하는 함수에 세션을 넘겨준다
    finally:
        db.close()        # 성공하든 실패하든 반드시 닫는다