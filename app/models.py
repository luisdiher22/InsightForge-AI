from sqlalchemy import Column, Integer, String, Float,DateTime,ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String)
    category = Column(String, nullable=True)
    quantity = Column(Integer)
    revenue = Column(Float)

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    dataset_type = Column(String)
    business_description = Column(String)
    column_mapping = Column(JSON, nullable=True)
    detected_fields = Column(JSON, nullable=True)
    available_kpis = Column(JSON, nullable=True)
    available_charts = Column(JSON, nullable=True)
    validation_summary = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    rows = relationship("DatasetRow", back_populates="dataset")

class DatasetRow(Base):
    __tablename__ = "dataset_rows"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    row_data = Column(JSON)

    dataset = relationship("Dataset", back_populates="rows")