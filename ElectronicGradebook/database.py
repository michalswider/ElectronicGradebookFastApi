from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

POSTGRESQL_DATABASE_URL = os.getenv("POSTGRESQL_DATABASE_URL")

engine = create_engine(POSTGRESQL_DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
