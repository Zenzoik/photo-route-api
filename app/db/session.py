from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 1) создаём асинхронный engine
engine = create_async_engine(
    settings.database_url,
    echo=True,           # лог SQL-запросов в консоль (на проде можно отключить)
)

# 2) фабрика сессий
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False,)

# 3) зависимость для FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
