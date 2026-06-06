import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# I default to SQLite so the project can run locally without extra services.
# Set DATABASE_URL to use PostgreSQL in production or when you want a shared DB.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sales_kpi.db")

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
	engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()