# app/services/exif_service.py

from PIL import Image
import pillow_heif
import piexif

pillow_heif.register_heif_opener()


def dms_to_decimal(dms: tuple, ref: bytes) -> float:
    """
    Преобразует GPS-координаты из формата DMS (Degrees, Minutes, Seconds)
    в десятичные градусы.
    dms — это кортеж из трёх элементов ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den)),
    ref — байтовая строка: b'N', b'S', b'E' или b'W'.
    """
    deg_num, deg_den = dms[0]
    min_num, min_den = dms[1]
    sec_num, sec_den = dms[2]

    degrees = deg_num / deg_den
    minutes = min_num / min_den
    seconds = sec_num / sec_den

    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in (b'S', b'W'):
        decimal = -decimal
    return decimal


def parse_exif_coords(path: str) -> tuple[float, float]:
    """
    Открывает изображение (JPEG, HEIC и т.д.) через PIL (с pillow_heif),
    читает EXIF через piexif, извлекает GPSLatitude/GPSLongitude,
    возвращает (lat, lng) в десятичных градусах.
    """
    img = Image.open(path)

    exif_bytes = img.info.get("exif")
    if not exif_bytes:
        raise ValueError("No EXIF metadata found")

    exif_dict = piexif.load(exif_bytes)

    gps_ifd = exif_dict.get("GPS", {})
    lat_dms = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
    lat_ref = gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef)
    lng_dms = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
    lng_ref = gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef)

    if not (lat_dms and lat_ref and lng_dms and lng_ref):
        raise ValueError("No GPS tags in EXIF")

    lat = dms_to_decimal(lat_dms, lat_ref)
    lng = dms_to_decimal(lng_dms, lng_ref)
    return lat, lng


def parse_exif_timestamp(path: str) -> str:
    """
    Извлекает дату-время съёмки (DateTimeOriginal) из EXIF.
    Возвращает строку формата "YYYY:MM:DD HH:MM:SS".
    """
    img = Image.open(path)
    exif_bytes = img.info.get("exif")
    if not exif_bytes:
        raise ValueError("No EXIF metadata found")

    exif_dict = piexif.load(exif_bytes)

    dt_bytes = exif_dict["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
    if not dt_bytes:
        dt_bytes = exif_dict["0th"].get(piexif.ImageIFD.DateTime)
        if not dt_bytes:
            raise ValueError("No DateTimeOriginal in EXIF")

    datetime_str = dt_bytes.decode("utf-8")
    return datetime_str


def parse_exif_coords_and_time(path: str) -> tuple[float, float, str]:
    """
    Удобная обёртка, возвращает (lat, lng, datetime_str).
    """
    lat, lng = parse_exif_coords(path)
    dt = parse_exif_timestamp(path)
    return lat, lng, dt
