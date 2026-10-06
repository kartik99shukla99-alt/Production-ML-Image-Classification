from fastapi import FastAPI, HTTPException, status
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.status import router as status_router
from app.api.upload import router as upload_router
from app.cache.redis_cache import redis_health_check
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }

@app.get("/ready")
async def ready():
    redis_ok = redis_health_check()

    if not redis_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "redis": "unavailable",
            },
        )
    
    return {
        "status": "ready",
        "redis": "connected",
    }


app.include_router(upload_router)
app.include_router(status_router)
