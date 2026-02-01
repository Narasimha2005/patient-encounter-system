"""
Database
"""

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# =========================
# DATABASE ENGINE
# =========================
engine = create_engine(
    "mysql+pymysql://mongouhd_evernorth:U*dgQkKRuEHe@cp-15.webhostbox.net/mongouhd_evernorth?charset=utf8mb4",
    echo=True,  # Shows generated SQL (useful for learning)
)

SessionLocal = sessionmaker(bind=engine)

# =========================
# BASE CLASS
# =========================


class Base(DeclarativeBase):
    pass


# =========================
# CREATE TABLES
# =========================

# NOTE: Use Alembic for production systems
Base.metadata.create_all(engine)
