from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "db_connected": True
    }
