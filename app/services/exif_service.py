# app/services/exif_service.py

import piexif
from PIL import Image
from app.utils.gps import dms_to_decimal
import pillow_heif
pillow_heif.register_heif_opener()

def parse_exif_coords(path: str) -> tuple[float, float]:
    """
    Открывает изображение (JPEG или HEIC), читает EXIF и возвращает (lat, lng).
    Бросает ValueError, если GPS-тегов нет.
    """
    img = Image.open(path)

    # 1) Попробуем получить «сырые» EXIF-байты
    exif_bytes = None

    # Для JPEG: img.info.get("exif") обычно содержит байты
    if "exif" in img.info:
        exif_bytes = img.info["exif"]
    else:
        # Для HEIC и других форматов: используем .getexif(), если есть
        try:
            exif = img.getexif()
            # .tobytes() вернёт байты EXIF
            exif_bytes = exif.tobytes()
        except Exception:
            exif_bytes = None

    if not exif_bytes:
        raise ValueError("No EXIF metadata found")

    # 2) Загружаем словарь EXIF
    exif_dict = piexif.load(exif_bytes)
    gps_ifd = exif_dict.get("GPS", {})

    # 3) Извлекаем нужные теги
    lat_dms = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
    lat_ref = gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef)
    lng_dms = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
    lng_ref = gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef)

    if not (lat_dms and lat_ref and lng_dms and lng_ref):
        raise ValueError("No GPS tags in EXIF")

    # 4) Конвертация D/M/S → десятичные градусы
    lat = dms_to_decimal(lat_dms, lat_ref)
    lng = dms_to_decimal(lng_dms, lng_ref)
    return lat, lng
