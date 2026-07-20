from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.lifespan import lifespan
from app.presentation.routers.categories import router as categories_router
from app.presentation.routers.users import router as users_router

app = FastAPI(title="FastAPI Интернет-магазин", lifespan=lifespan)

app.include_router(users_router)
app.include_router(categories_router)


app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root() -> dict:
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}
