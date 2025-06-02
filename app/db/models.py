# app/db/models.py

from sqlalchemy import Column, Integer, Text, DateTime
from geoalchemy2 import Geometry
from app.db.base import Base

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
