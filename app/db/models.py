# app/db/models.py

from sqlalchemy import Column, Integer, Text, DateTime
from geoalchemy2 import Geometry
from app.db.base import Base

class Photo(Base):
    __tablename__ = "photos"

    # PK — автоматически инкрементируется
    id = Column(Integer, primary_key=True, index=True)
    # имя файла — текст, не может быть пустым
    filename = Column(Text, nullable=False)
    # время загрузки или съёмки
    timestamp = Column(DateTime, nullable=False)
    # геометрия POINT (lat/lng), SRID=4326
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
