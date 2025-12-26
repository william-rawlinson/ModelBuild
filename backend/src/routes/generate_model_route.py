import asyncio
import uuid
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.src.model_generation.bundling.generate_model_bundle import generate_model_bundle
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
    model_description: str
    disc_rate_cost_annual: Any
    disc_rate_qaly_annual: Any
    time_horizon_years: Any
    cycle_length_years: Any
    wtp_threshold: Any
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

    job_id = uuid.uuid4().hex

    treatments = [req.intervention] + req.comparators

    async def _runner():
        try:
            await generate_model_bundle(model_description=req.model_description,
                                        treatments=treatments, data_points=req.data_points, time_horizon_years=req.time_horizon_years,
                                        cycle_length_years=req.cycle_length_years, disc_rate_cost_annual=req.disc_rate_cost_annual,
                                        disc_rate_qaly_annual=req.disc_rate_qaly_annual)
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
