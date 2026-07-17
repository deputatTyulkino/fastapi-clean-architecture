from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine, session_factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session_factory = session_factory
    yield
    await engine.dispose()
