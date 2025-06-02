# app/crud/photo.py

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Photo


async def create_photo(db: AsyncSession, filename: str, lat: float, lng: float, timestamp: datetime, owner_token: str):
    """
    Сохраняет новую запись о фото в базу:
    filename: имя файла,
    lat, lng: координаты,
    timestamp: дата-время из EXIF.
    """
    point_wkt = f"SRID=4326;POINT({lng} {lat})"

    # Создаём объект модели
    photo_obj = Photo(
        filename=filename,
        timestamp=timestamp,
        geom=point_wkt,
        owner_token=owner_token
    )
    db.add(photo_obj)
    await db.commit()
    await db.refresh(photo_obj)
    return photo_obj



async def get_photos_by_owner(db: AsyncSession, owner_token: str):
    query = select(Photo).where(Photo.owner_token == owner_token).order_by(Photo.timestamp)
    result = await db.execute(query)
    return result.scalars().all()


async def get_photos(db: AsyncSession) -> list[Photo]:
    """
    Возвращает все объекты Photo, отсортированные по timestamp.
    """
    result = await db.execute(select(Photo).order_by(Photo.timestamp))
    return result.scalars().all()