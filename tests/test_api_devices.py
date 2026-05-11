import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.models import SystemEvent


class TestPostDeviceCommand:
    async def test_fan_on_command_returns_200(self, client, mock_db):
        """POST /api/devices/fan/command with valid body → 200 + correct JSON."""
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with patch("api.routes_device.publish_command"):
            response = await client.post(
                "/api/devices/fan/command",
                json={"action": "on", "value": 32.0},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["device"] == "fan"
        assert body["action"] == "on"
        assert body["node_id"] == 1

    async def test_fan_on_command_calls_publish_command(self, client, mock_db):
        """POST fan/on → publish_command('fan', 'on', 32.0) called exactly once."""
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with patch("api.routes_device.publish_command") as mock_pub:
            await client.post(
                "/api/devices/fan/command",
                json={"action": "on", "value": 32.0},
            )

        mock_pub.assert_called_once_with("fan", "on", 32.0)

    async def test_fan_on_command_persists_to_db(self, client, mock_db):
        """POST fan/on → db.add() and db.commit() both called."""
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with patch("api.routes_device.publish_command"):
            await client.post(
                "/api/devices/fan/command",
                json={"action": "on", "value": 32.0},
            )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    async def test_light_on_command_calls_publish_command(self, client, mock_db):
        """POST light/on with low-light value → publish_command('light', 'on', 150.0)."""
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with patch("api.routes_device.publish_command") as mock_pub:
            await client.post(
                "/api/devices/light/command",
                json={"action": "on", "value": 150.0},
            )

        mock_pub.assert_called_once_with("light", "on", 150.0)

    async def test_command_without_value_ok(self, client, mock_db):
        """value is optional — POST with no value still succeeds."""
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with patch("api.routes_device.publish_command") as mock_pub:
            response = await client.post(
                "/api/devices/fan/command",
                json={"action": "off"},
            )

        assert response.status_code == 200
        mock_pub.assert_called_once_with("fan", "off", None)

    async def test_custom_node_id_propagated(self, client, mock_db):
        """node_id in body overrides settings.NODE_ID."""
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with patch("api.routes_device.publish_command"):
            response = await client.post(
                "/api/devices/fan/command",
                json={"action": "on", "node_id": 42},
            )

        assert response.json()["node_id"] == 42


class TestGetDeviceEvents:
    async def test_get_events_returns_list(self, client, mock_db):
        """GET /api/devices/events → list of event dicts."""
        row = SystemEvent(
            timestamp=datetime(2026, 5, 10, 12, 0, 0),
            node_id=1,
            event_type="fan_on",
            trigger_source="manual",
            target_device="fan",
            value=32.0,
        )
        row.event_id = 1

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [row]
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/devices/events")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["event_type"] == "fan_on"
        assert data[0]["target_device"] == "fan"
        assert data[0]["node_id"] == 1

    async def test_get_events_empty_db(self, client, mock_db):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await client.get("/api/devices/events")

        assert response.status_code == 200
        assert response.json() == []
