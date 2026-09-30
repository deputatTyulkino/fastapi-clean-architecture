from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.infrastructure.database.connect import engine, session_factory
from app.infrastructure.depends.utils.redis_depends import get_redis_manager_infr
from app.presentation.routers.cart_items import router as cart_items_router
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


@app.exception_handler(HTTPException)
async def http_exceptions_handlers(exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"success": False, "detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exceptions_handlers(exc: ValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"success": False, "detail": message},
    )


app.include_router(users_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(sellers_router)
app.include_router(cart_items_router)


app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root() -> dict:
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}


@app.get("/health", status_code=200)
async def health():
    return True
