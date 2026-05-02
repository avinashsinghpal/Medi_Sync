from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "db_connected": True  # In a real implementation, this would check the actual DB connection
    }
