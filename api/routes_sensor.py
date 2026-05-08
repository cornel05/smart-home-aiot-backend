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
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "timestamp": r.timestamp,
            "node_id": r.node_id,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "light_intensity": r.light_intensity,
            "gas_ppm": r.gas_ppm,
            "door_open": r.door_open,
        }
        for r in rows
    ]


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
            "gas_ppm": r.gas_ppm,
            "door_open": r.door_open,
        }
        for r in rows
    ]
