# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DB_URL = os.getenv("DB_URL", "sqlite:///alerts.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    location = Column(String)
    city = Column(String)
    severity = Column(String)
    message = Column(String)
    metadata = Column(JSON)

Base.metadata.create_all(engine)