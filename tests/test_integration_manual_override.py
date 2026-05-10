"""
Integration test: Manual Override flow (Module 3).

Flow under test:
  User clicks 'Turn Fan ON' → Controls.jsx sendCommand("fan", "on")
  → POST /api/devices/fan/command {"action": "on"}
  → Backend: publish_command("fan", "on", None)           [MQTT publish]
  → Backend: INSERT system_events trigger_source='manual' [DB log]

External boundary mocked: mqtt.publisher.publish_command (no real broker)
Real: HTTP routing, request validation, DB session, SQLAlchemy ORM writes
"""
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from database.models import Base, NodeMetadata, SystemEvent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session():
    """
    SQLite in-memory DB with the real SQLAlchemy schema.
    Seeds node_metadata.node_id=1 to satisfy FK constraints.
    Torn down after each test.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as seed:
        seed.add(NodeMetadata(node_id=1, location="test_room", status="active"))
        await seed.commit()

    yield factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client_and_mqtt(db_session):
    """
    FastAPI AsyncClient wired to the real SQLite DB.
    Yields (http_client, mock_publish, db_session_factory).
    """
    from main import app
    from database.session import get_db

    async def _real_db():
        async with db_session() as session:
            yield session

    app.dependency_overrides[get_db] = _real_db

    with (
        patch("api.routes_device.publish_command") as mock_publish,
        patch("main.init_db", new=AsyncMock()),
        patch("mqtt.subscriber.start_subscriber", return_value=None),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as http:
            yield http, mock_publish, db_session

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestManualOverrideFanOn:
    """Full integration: user presses 'Turn Fan ON' on the Dashboard."""

    async def test_api_contract_request_accepted(self, client_and_mqtt):
        """Frontend POST hits correct endpoint; response matches expected shape."""
        http, _, _ = client_and_mqtt
        response = await http.post(
            "/api/devices/fan/command", json={"action": "on"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["device"] == "fan"
        assert body["action"] == "on"
        assert body["node_id"] == 1

    async def test_mqtt_actuator_packet_published(self, client_and_mqtt):
        """Backend publishes exactly one MQTT command with correct device/action."""
        http, mock_publish, _ = client_and_mqtt
        await http.post("/api/devices/fan/command", json={"action": "on"})
        mock_publish.assert_called_once_with("fan", "on", None)

    async def test_event_logged_to_db_with_manual_source(self, client_and_mqtt):
        """SystemEvent row persisted; trigger_source='manual', event_type='fan_on'."""
        http, _, db_session = client_and_mqtt
        await http.post("/api/devices/fan/command", json={"action": "on"})

        async with db_session() as session:
            result = await session.execute(select(SystemEvent))
            events = result.scalars().all()

        assert len(events) == 1
        ev = events[0]
        assert ev.trigger_source == "manual"
        assert ev.target_device == "fan"
        assert ev.event_type == "fan_on"
        assert ev.node_id == 1
        assert ev.value is None

    async def test_rule_engine_not_invoked(self, client_and_mqtt):
        """Manual override bypasses automatic rule evaluation entirely."""
        http, _, _ = client_and_mqtt
        with patch("services.rule_engine.evaluate") as mock_eval:
            await http.post("/api/devices/fan/command", json={"action": "on"})
        mock_eval.assert_not_called()

    async def test_exactly_one_event_per_command(self, client_and_mqtt):
        """Single POST → exactly one DB row; no duplicate logging."""
        http, _, db_session = client_and_mqtt
        await http.post("/api/devices/fan/command", json={"action": "on"})

        async with db_session() as session:
            result = await session.execute(select(SystemEvent))
            events = result.scalars().all()
        assert len(events) == 1
