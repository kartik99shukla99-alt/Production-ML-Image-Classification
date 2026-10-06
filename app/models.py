from pydantic import BaseModel, Field
from typing import Literal

class Prediction(BaseModel):
    class_name : str
    confidence : float = Field(ge = 0.0, le = 1.0) #ge(>=0) and le(<=1) means min 0 and max 1

class PredictionResponse(BaseModel):
    task_id: str
    status: Literal["SUCCESS","FAILED","PENDING","PROCESSING"]
    predictions: list[Prediction] = Field(default_factory=list)

class TaskStatusResponse(BaseModel):
    task_id: str
    status: Literal["SUCCESS","FAILED","PENDING","PROCESSING"]
    message: str |None= None

class ErrorResponse(BaseModel):
    error:str
    message:str
    details: dict | None = None

