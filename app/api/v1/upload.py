from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
import shutil
from sqlalchemy import text
from app.services.exif_service import parse_exif_coords
from app.crud.photo import create_photo, get_photos
from app.db.session import get_db
from app.schemas.photo import PhotoOut, RoutePoint

router = APIRouter()

@router.post("/upload/", response_model=PhotoOut)
async def upload_image(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    # сохраняем файл
    local_path = f"uploads/{file.filename}"
    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # парсим EXIF
    try:
        lat, lng = parse_exif_coords(local_path)
    except Exception:
        raise HTTPException(status_code=400, detail="No GPS data found")

    # сохраняем в БД
    photo = await create_photo(db, file.filename, lat, lng)
    return {
        "id":        photo.id,
        "filename":  photo.filename,
        "timestamp": photo.timestamp,
        "lat":       lat,
        "lng":       lng,
    }



@router.get("/photos/", response_model=list[PhotoOut])
async def list_photos(db = Depends(get_db)):
    # 1) Выполняем чистый SQL с функциями ST_Y (lat) и ST_X (lng)
    query = text("""
        SELECT
            id,
            filename,
            timestamp,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lng
        FROM photos
        ORDER BY timestamp
    """)
    result = await db.execute(query)
    rows = result.all()  # список кортежей (id, filename, timestamp, lat, lng)

    # 2) Преобразуем в список словарей
    return [
        {
            "id":        r[0],
            "filename":  r[1],
            "timestamp": r[2],
            "lat":       r[3],
            "lng":       r[4],
        }
        for r in rows
    ]

@router.delete("/photos/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_photos(db = Depends(get_db)):
    # Удаляем все записи
    await db.execute(text("TRUNCATE TABLE photos"))
    await db.commit()
    # Очищаем папку uploads
    import os, glob
    for f in glob.glob("uploads/*"):
        os.remove(f)
    return

@router.get("/route/", response_model=list[RoutePoint])
async def get_route(db = Depends(get_db)):
    query = text("""
        SELECT
            filename,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lng,
            timestamp AS time
        FROM photos
        ORDER BY timestamp
    """)
    res = await db.execute(query)
    rows = res.all()  # [(filename, lat, lng, time), ...]

    return [
        {
            "filename": r[0],
            "lat":      r[1],
            "lng":      r[2],
            "time":     r[3],
        }
        for r in rows
    ]

