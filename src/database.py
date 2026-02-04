"""
Database
"""

import os

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
)

# loading variables from .env file
load_dotenv()

from sqlalchemy.orm import DeclarativeBase, sessionmaker  # noqa: E402

# =========================
# DATABASE ENGINE
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Shows generated SQL (useful for learning)
)

SessionLocal = sessionmaker(bind=engine)

# =========================
# BASE CLASS
# =========================


class Base(DeclarativeBase):
    pass
