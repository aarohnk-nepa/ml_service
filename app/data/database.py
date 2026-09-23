from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME

def _build_engine():
    """
    database engine builder
    """
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(
        DATABASE_URL,
        pool_size=1,
        max_overflow=0,
        pool_timeout=30,
        pool_pre_ping=True,
    )

    SessionLocal = sessionmaker(bind=engine)

    _test_connection(engine)

    return engine



def _test_connection(engine):
    """
    test connection to database
    """
    try:
        with engine.connect() as conn:
            version = conn.scalar(text("SELECT version();"))
            print(f"connected successfully; version {version}")
    except Exception as e:
        print(f"connection failed; reason {e}")
        raise


engine = _build_engine()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)