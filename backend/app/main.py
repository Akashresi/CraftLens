import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.config import settings

UPLOAD_DIR = "./uploads"
os.makedirs(f"{UPLOAD_DIR}/original", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/processed", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup
    yield
    # App shutdown


app = FastAPI(
    title=settings.APP_NAME,
    description="Production API for CraftLens 2.0 - AI-Powered Artisan Business Management and Global Marketplace Platform.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static media serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include master API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
        "status": "operational",
    }
