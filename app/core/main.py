from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.infrastructure.database.connect import engine, session_factory
from app.infrastructure.depends.utils.redis_depends import get_redis_manager_infr
from app.presentation.routers.categories import router as categories_router
from app.presentation.routers.products import router as products_router
from app.presentation.routers.sellers import router as sellers_router
from app.presentation.routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session_factory = session_factory
    redis_manager = get_redis_manager_infr()
    await redis_manager.init()
    yield
    await engine.dispose()
    await redis_manager.close()


app = FastAPI(title="FastAPI Интернет-магазин", lifespan=lifespan)

app.include_router(users_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(sellers_router)


app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root() -> dict:
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}
