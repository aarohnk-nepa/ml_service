import os
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker


DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

DATABASE_URL = F"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=0,
    pool_timeout=30,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(bind=engine)

def test_connection():
    """
    test connection to database
    """
    with SessionLocal() as session:
        try:
            result = session.scalar(text("SELECT version();"))
            print(f"connected successfully; version {result}")
        except Exception as e:
            print(f"connection failed; reason {e}")

test_connection()
