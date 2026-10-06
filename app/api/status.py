from celery.result import AsyncResult
from fastapi import APIRouter

from app.models import PredictionResponse
from app.tasks.classification import celery_app

router = APIRouter(
    prefix="/v1",
    tags=["Predictions"],
)


@router.get("/predictions/{task_id}", response_model=PredictionResponse)
async def get_prediction_status(task_id: str) -> PredictionResponse:
    task = AsyncResult(task_id, app=celery_app)

    if task.state == "SUCCESS":
        result = task.result or {}
        return PredictionResponse(
            task_id=task_id,
            status="SUCCESS",
            predictions=result.get("predictions", []),
        )

    if task.state == "FAILURE":
        return PredictionResponse(
            task_id=task_id,
            status="FAILED",
            predictions=[],
        )

    if task.state in ("STARTED", "PROCESSING", "RETRY"):
        return PredictionResponse(
            task_id=task_id,
            status="PROCESSING",
            predictions=[],
        )

    return PredictionResponse(
        task_id=task_id,
        status="PENDING",
        predictions=[],
    )
