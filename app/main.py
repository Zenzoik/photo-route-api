# app/main.py

import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.db.base import Base
from app.db.session import engine
from app.api.v1.upload import router as upload_router

app = FastAPI(title="Photo→Route API")
app.include_router(upload_router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # отдаём просто HTML, JS подхватит маршрут
    return templates.TemplateResponse("map.html", {"request": request})

async def init_models():
    """
    Создаёт все таблицы, описанные в Base.metadata,
    если их ещё нет в базе.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    # 1) инициализируем модели (создаём схему)
    asyncio.run(init_models())
    # 2) запускаем сервер
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
