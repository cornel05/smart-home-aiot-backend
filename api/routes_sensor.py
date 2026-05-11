from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.models import SensorTelemetry

router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.get("/latest")
async def get_latest(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=10, le=100),
):
    result = await db.execute(
        select(SensorTelemetry)
        .order_by(SensorTelemetry.timestamp.desc())
        .limit(max(limit * 4, 20))
    )
    rows = result.scalars().all()
    if not rows:
        return []

    temperature = next((r.temperature for r in rows if r.temperature is not None), None)
    humidity = next((r.humidity for r in rows if r.humidity is not None), None)
    light_intensity = next((r.light_intensity for r in rows if r.light_intensity is not None), None)

    return [{
        "timestamp": rows[0].timestamp,
        "node_id": rows[0].node_id,
        "temperature": temperature,
        "humidity": humidity,
        "light_intensity": light_intensity,
    }]


@router.get("/history")
async def get_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    minutes: int = Query(default=60, le=1440),
    node_id: int = Query(default=1),
):
    since = datetime.utcnow() - timedelta(minutes=minutes)
    result = await db.execute(
        select(SensorTelemetry)
        .where(SensorTelemetry.timestamp >= since)
        .where(SensorTelemetry.node_id == node_id)
        .order_by(SensorTelemetry.timestamp.asc())
    )
    rows = result.scalars().all()
    return [
        {
            "timestamp": r.timestamp,
            "node_id": r.node_id,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "light_intensity": r.light_intensity,
        }
        for r in rows
    ]
