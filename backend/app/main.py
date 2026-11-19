from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.config import settings
from app.services.keitaro import KeitaroClient, create_keitaro_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client: KeitaroClient | None = create_keitaro_client()
    app.state.keitaro = client
    try:
        yield
    finally:
        if client is not None:
            await client.aclose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
