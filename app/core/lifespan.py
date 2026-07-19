from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database.connect import engine, session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session_factory = session_factory
    yield
    await engine.dispose()
