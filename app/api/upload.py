from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.cache.metrics import (
    cache_hits,
    cache_misses
)

from app.cache.redis_cache import (
    generate_image_hash,
    get_cached_prediction,
)

from app.models import PredictionResponse
from app.services.image_service import (
    ImageValidationError,
    validate_image,
)

from app.services.storage_service import save_image
from app.tasks.classification import classify_image

router = APIRouter(
    prefix="/v1",
    tags=["Predictions"],
)

@router.post(
    "/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_prediction(
    file: UploadFile = File(...)
):

    try:
        image_bytes = await validate_image(file)

    except ImageValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # Generate image hash
    image_hash = generate_image_hash(image_bytes)

    cached_prediction = get_cached_prediction(image_hash)

    # CACHE HIT

    if cached_prediction is not None:
        cache_hits.inc()

        return PredictionResponse(
            task_id=str(uuid4()),
            status="SUCCESS",
            predictions=cached_prediction["predictions"],
        )

    # CACHE MISS
    cache_misses.inc()
    
    task_id = str(uuid4())

    image_path = save_image(
        task_id,
        image_bytes,
    )

    classify_image.apply_async(
        args=[image_path, image_hash],
        task_id=task_id,
    )

    return PredictionResponse(
        task_id=task_id,
        status="PENDING",
        predictions=[],
    )

