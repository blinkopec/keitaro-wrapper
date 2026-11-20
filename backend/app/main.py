from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.main import api_router
from app.config import settings
from app.services.keitaro import (
    KeitaroClient,
    KeitaroError,
    KeitaroNotConfigured,
    KeitaroNotFound,
    create_keitaro_client,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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


@app.exception_handler(KeitaroNotConfigured)
async def keitaro_not_configured_handler(
    request: Request, exc: KeitaroNotConfigured
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
    )


@app.exception_handler(KeitaroNotFound)
async def keitaro_not_found_handler(request: Request, exc: KeitaroNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(KeitaroError)
async def keitaro_error_handler(request: Request, exc: KeitaroError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc)},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
