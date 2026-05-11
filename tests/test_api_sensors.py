import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.models import SensorTelemetry


def _make_sensor_row(temperature: float, light_intensity: float) -> SensorTelemetry:
    return SensorTelemetry(
        timestamp=datetime(2026, 5, 10, 12, 0, 0),
        node_id=1,
        temperature=temperature,
        humidity=65.0,
        light_intensity=light_intensity,
    )


class TestGetSensorsLatest:
    async def test_returns_list_with_correct_shape(self, client, mock_db):
        """GET /api/sensors/latest → list of sensor dicts with all required keys."""
        rows = [
            _make_sensor_row(temperature=32.5, light_intensity=150.0),
            _make_sensor_row(temperature=25.0, light_intensity=500.0),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = rows
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/sensors/latest")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert set(data[0].keys()) == {"timestamp", "node_id", "temperature", "humidity", "light_intensity"}

    async def test_high_temp_row_values_preserved(self, client, mock_db):
        """temperature=32.5 (>30°C) and light=150.0 (<200 Lux) stored correctly."""
        rows = [_make_sensor_row(temperature=32.5, light_intensity=150.0)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = rows
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/sensors/latest")

        data = response.json()
        assert data[0]["temperature"] == 32.5
        assert data[0]["light_intensity"] == 150.0

    async def test_empty_db_returns_empty_list(self, client, mock_db):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/sensors/latest")

        assert response.status_code == 200
        assert response.json() == []

    async def test_limit_query_param_accepted(self, client, mock_db):
        """limit=1 query param — route accepts it without error."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/sensors/latest?limit=1")

        assert response.status_code == 200

    async def test_limit_over_100_rejected(self, client, mock_db):
        """limit > 100 violates le=100 constraint → 422."""
        response = await client.get("/api/sensors/latest?limit=101")

        assert response.status_code == 422


class TestGetSensorsHistory:
    async def test_returns_list(self, client, mock_db):
        rows = [_make_sensor_row(temperature=31.0, light_intensity=180.0)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = rows
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/sensors/history?minutes=30&node_id=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["temperature"] == 31.0

    async def test_minutes_over_1440_rejected(self, client, mock_db):
        """minutes > 1440 violates le=1440 → 422."""
        response = await client.get("/api/sensors/history?minutes=9999")

        assert response.status_code == 422
