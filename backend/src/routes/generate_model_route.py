import asyncio
import uuid
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.src.services.generate_model_service import generate_model_dummy
from backend.websockets.websocket_manager import manager

router = APIRouter()
logger = logging.getLogger(__name__)

PROCESS_NAME = "generate_model"


class TimeSetting(BaseModel):
    value: float
    unit: str


class GenerateModelRequest(BaseModel):
    intervention: str
    comparators: List[str]
    health_states: List[str]
    time_horizon: TimeSetting
    cycle_length: TimeSetting
    model_description: str
    data_points: List[Dict[str, Any]] = Field(default_factory=list)


class GenerateModelResponse(BaseModel):
    job_id: str
    status: str  # "started"


@router.post("/", response_model=GenerateModelResponse)
async def generate_model(req: GenerateModelRequest):
    # Minimal validation (keep v1 light)
    if not req.model_description.strip():
        raise HTTPException(status_code=422, detail="model_description is required.")
    if not req.intervention.strip():
        raise HTTPException(status_code=422, detail="intervention is required.")
    if len(req.comparators) < 1:
        raise HTTPException(status_code=422, detail="At least one comparator is required.")
    if len(req.health_states) < 2:
        raise HTTPException(status_code=422, detail="health_states must have at least 2 states.")

    job_id = uuid.uuid4().hex

    async def _runner():
        try:
            await generate_model_dummy(req.model_dump())
        except Exception as e:
            logger.exception("generate_model failed (job_id=%s)", job_id)
            # Push an error to the UI log and mark complete
            try:
                await manager.send_message(
                    message_type="progress",
                    payload={"message": f"❌ Generation failed: {type(e).__name__}: {e}"},
                    process_name=PROCESS_NAME,
                    process_complete=True,
                )
            except Exception:
                logger.exception("Failed to send WS error message")

    asyncio.create_task(_runner())

    return GenerateModelResponse(job_id=job_id, status="started")
