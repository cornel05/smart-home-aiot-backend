from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from database.session import get_db
from database.models import SystemEvent
from mqtt.publisher import publish_command

router = APIRouter(prefix="/devices", tags=["devices"])


class CommandRequest(BaseModel):
    action: str
    node_id: int | None = None
    value: float | None = None


@router.post("/{device_id}/command")
async def send_command(
    device_id: str,
    body: CommandRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    publish_command(device_id, body.action, body.value)
    node_id = body.node_id or settings.NODE_ID

    event = SystemEvent(
        timestamp=datetime.utcnow(),
        node_id=node_id,
        event_type=f"{device_id}_{body.action}",
        trigger_source="manual",
        target_device=device_id,
        value=body.value,
    )
    db.add(event)
    await db.commit()

    return {"status": "ok", "device": device_id, "action": body.action, "node_id": node_id}


@router.get("/events")
async def get_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
):
    from sqlalchemy import select
    result = await db.execute(
        select(SystemEvent).order_by(SystemEvent.timestamp.desc()).limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "event_id": r.event_id,
            "timestamp": r.timestamp,
            "node_id": r.node_id,
            "event_type": r.event_type,
            "trigger_source": r.trigger_source,
            "target_device": r.target_device,
            "value": r.value,
        }
        for r in rows
    ]
