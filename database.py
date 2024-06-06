import os
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session ,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

Base = declarative_base()

load_dotenv(os.getenv("ENV_FILE", ".env"))

engine = create_engine(os.environ["DATABASE_URL"])

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
get_db = Annotated[Session, Depends(_get_db)]
