import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request, Path
import shutil

from geoalchemy2.shape import to_shape
from sqlalchemy import delete, text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Photo
from app.services.exif_service import parse_exif_coords_and_time
from app.crud.photo import create_photo, get_photos_by_owner
from app.db.session import get_db
from app.schemas.photo import PhotoOut, RoutePoint


router = APIRouter()

@router.post("/uploadfiles/")
async def upload_files(request: Request,files: list[UploadFile], db = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    for file in files:
        user_folder = os.path.join("uploads", session_token)
        os.makedirs(user_folder, exist_ok=True)
        local_path = os.path.join(user_folder, file.filename)
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            lat, lng, timestamp_str = parse_exif_coords_and_time(local_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        timestamp = datetime.strptime(timestamp_str, "%Y:%m:%d %H:%M:%S")
        await create_photo(db, file.filename, lat, lng, timestamp, session_token)
    return {
        "message": "Files uploaded successfully."
    }

@router.post("/upload/", response_model=PhotoOut)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    db = Depends(get_db),
):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_folder = os.path.join("uploads", session_token)
    os.makedirs(user_folder, exist_ok=True)
    local_path = os.path.join(user_folder, file.filename)
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        lat, lng, timestamp_str = parse_exif_coords_and_time(local_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    timestamp = datetime.strptime(timestamp_str, "%Y:%m:%d %H:%M:%S")

    photo = await create_photo(db, file.filename, lat, lng, timestamp, session_token)
    return {
        "id":        photo.id,
        "filename":  photo.filename,
        "timestamp": photo.timestamp,
        "lat":       lat,
        "lng":       lng,
        "owner_token": session_token
    }



@router.get("/photos/", response_model=list[PhotoOut])
async def list_photosb(request: Request, db=Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    photos = await get_photos_by_owner(db, session_token)

    result = []
    for p in photos:
        point = to_shape(p.geom)
        lat = point.y
        lng = point.x

        result.append({
            "id":          p.id,
            "filename":    p.filename,
            "timestamp":   p.timestamp,
            "lat":         float(lat),
            "lng":         float(lng),
            "owner_token": p.owner_token
        })
    return result

@router.get("/photos/{photo_id}", response_model=PhotoOut)
async def get_photo(request: Request,photo_id: int, db=Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    photo = await db.execute(text("SELECT * FROM photos WHERE id = :photo_id AND owner_token = :session_token"), {"photo_id": photo_id, "session_token": session_token})
    photo = photo.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.delete("/photos/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_photos(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Удаление всех фотографий только текущего пользователя (по session_token).
    """
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # 1) Удаляем все записи из таблицы photos, принадлежащие этому токену
    await db.execute(delete(Photo).where(Photo.owner_token == session_token))
    await db.commit()

    # 2) Удаляем папку uploads/<session_token> целиком (со всеми файлами внутри)
    user_folder = os.path.join("uploads", session_token)
    if os.path.isdir(user_folder):
        try:
            shutil.rmtree(user_folder)
        except OSError:
            pass

    return None

@router.get("/route/", response_model=list[RoutePoint])
async def get_route(request: Request, db=Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    photos = await get_photos_by_owner(db, session_token)

    points = []
    for p in photos:
        point = to_shape(p.geom)
        points.append({
            "filename": p.filename,
            "lat": float(point.y),
            "lng": float(point.x),
            "time": p.timestamp,
            "owner_token": p.owner_token
        })
    return points

@router.get("/shared_route/{share_token}", response_model=list[RoutePoint])
async def shared_route(
    share_token: str = Path(..., description="Session token для шаринга маршрута"),
    db: AsyncSession = Depends(get_db)
):
    """
    Публичный эндпоинт: возвращает список точек маршрута
    для заданного токена (share_token), без проверки куки.
    """
    result = await db.execute(
        select(Photo).where(Photo.owner_token == share_token).order_by(Photo.timestamp)
    )
    photos = result.scalars().all()

    if not photos:
        return []

    points = []
    for p in photos:
        point = to_shape(p.geom)
        points.append({
            "filename": p.filename,
            "lat":      float(point.y),
            "lng":      float(point.x),
            "time":     p.timestamp,
            "owner_token": p.owner_token,
        })
    return points


