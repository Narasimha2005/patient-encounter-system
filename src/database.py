"""
Database
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine(
    "sqlite:///./mems.db",
    echo=True,  # Shows generated SQL (useful for learning)
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
