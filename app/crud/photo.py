# app/crud/photo.py

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Photo

async def create_photo(db: AsyncSession, filename: str, lat: float, lng: float) -> Photo:
    """
    Сохраняет новую запись в таблицу photos и возвращает объект Photo.
    """
    point_wkt = f"SRID=4326;POINT({lng} {lat})"
    photo = Photo(
        filename=filename,
        timestamp=datetime.utcnow(),
        geom=point_wkt
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo

async def get_photos(db: AsyncSession) -> list[Photo]:
    """
    Возвращает все объекты Photo, отсортированные по timestamp.
    """
    result = await db.execute(select(Photo).order_by(Photo.timestamp))
    return result.scalars().all()
