from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from medisync.core.config import get_settings
from medisync.api.routers import health

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
