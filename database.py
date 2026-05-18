from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")

if not os.environ.get("DATABASE_URL"):
    # Ensure SQLite path exists
    db_path = DATABASE_URL.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
