import asyncio
from typing import Dict, Any

from backend.websockets.websocket_manager import manager

PROCESS_NAME = "generate_model"

async def generate_model_dummy(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder generator that emits progress over WS.
    """
    # Start
    await manager.send_message(
        message_type="process_start",
        payload={"message": "Starting model generation…"},
        process_name=PROCESS_NAME,
        process_complete=False,
    )

    steps = [
        "Validating inputs…",
        "Creating model skeleton…",
        "Building health state structure…",
        "Adding parameters…",
        "Finalising…",
    ]

    for i, msg in enumerate(steps, start=1):
        await manager.send_message(
            message_type="progress",
            payload={"message": f"[{i}/{len(steps)}] {msg}"},
            process_name=PROCESS_NAME,
            process_complete=False,
        )
        await asyncio.sleep(0.8)

    # Finish
    await manager.send_message(
        message_type="progress",
        payload={"message": "✅ Generation complete."},
        process_name=PROCESS_NAME,
        process_complete=True,
    )

    # Return a dummy result (not used yet)
    return {"status": "ok", "model_id": "dummy_model_001"}
