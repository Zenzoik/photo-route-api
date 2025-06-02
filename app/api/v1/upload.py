import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
import shutil

from geoalchemy2.shape import to_shape
from sqlalchemy import text
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
        # 1) Переведём p.geom (WKBElement) в shapely.geometry.Point
        point = to_shape(p.geom)
        # 2) Извлечём координаты из объекта Point
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

@router.delete("/photos/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_photos(db = Depends(get_db)):
    await db.execute(text("TRUNCATE TABLE photos"))
    await db.commit()
    import os, glob
    for f in glob.glob("uploads/*"):
        os.remove(f)
    return {"message": "Photos cleared successfully."}

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
            "time": p.timestamp
        })
    return points


