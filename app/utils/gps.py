# app/utils/gps.py

def dms_to_decimal(dms: tuple, ref: bytes | str) -> float:
    """
    Переводит координаты из EXIF-формата (DMS) в десятичные градусы.
    dms — кортеж трёх кортежей: ((deg_num, deg_den), (min_num, min_den), (sec_num, sec_den))
    ref — b'N', b'S', b'E' или b'W' (или строчного типа).
    """
    # Разбираем градусы, минуты, секунды
    deg = dms[0][0] / dms[0][1]
    minute = dms[1][0] / dms[1][1]
    sec = dms[2][0] / dms[2][1]

    decimal = deg + minute / 60 + sec / 3600
    # Если ref указывает на юг или запад — отрицательное значение
    if isinstance(ref, bytes):
        ref = ref.decode()
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal
