import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_db():
    """Fully mocked AsyncSession — no real DB needed."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
async def client(mock_db):
    """
    httpx AsyncClient pointed at the FastAPI app.
    - get_db overridden with mock_db
    - init_db and start_subscriber patched out (no DB or MQTT broker)
    """
    from main import app
    from database.session import get_db

    async def _override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_get_db

    with (
        patch("main.init_db", new=AsyncMock()),
        patch("mqtt.subscriber.start_subscriber", return_value=None),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as c:
            yield c

    app.dependency_overrides.clear()
