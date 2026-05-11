import logging
import asyncio
from datetime import datetime
import paho.mqtt.client as mqtt
from core.config import settings
from services.rule_engine import evaluate

logger = logging.getLogger(__name__)

_loop: asyncio.AbstractEventLoop | None = None


def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        for topic in _FEED_TO_FIELD:
            client.subscribe(topic)
        logger.info("MQTT subscriber connected to Adafruit IO feeds")
    else:
        logger.error("MQTT connect failed: %s", reason_code)


def _feed_topic(feed_key: str) -> str:
    return f"{settings.AIO_USERNAME}/feeds/{feed_key}"


_node_buffer: dict[int, dict] = {}

_FEED_TO_FIELD = {
    _feed_topic(settings.MQTT_TOPIC_TEMP): "temperature",
    _feed_topic(settings.MQTT_TOPIC_HUM): "humidity",
    _feed_topic(settings.MQTT_TOPIC_LIGHT): "light_intensity",
    _feed_topic(settings.MQTT_TOPIC_IR): "ir",
}


def _payload_from_feed(topic: str, raw_value: bytes) -> dict | None:
    field = _FEED_TO_FIELD.get(topic)
    if field is None:
        logger.warning("Dropping message from unexpected topic %s", topic)
        return None

    value = float(raw_value.decode())
    return {"node_id": settings.NODE_ID, field: value}


def _on_message(client, userdata, msg):
    try:
        payload = _payload_from_feed(msg.topic, msg.payload)
        if payload is None:
            return

        logger.info("Received %s: %s", msg.topic, payload)
        events = evaluate(payload)

        if _loop and not _loop.is_closed():
            asyncio.run_coroutine_threadsafe(_persist(payload, events), _loop)
    except Exception as exc:
        logger.exception("Error processing MQTT message: %s", exc)


async def _persist(payload: dict, events: list[dict]):
    from database.session import AsyncSessionLocal
    from database.models import SensorTelemetry, SystemEvent
    from core.config import settings as cfg

    node_id = payload.get("node_id", cfg.NODE_ID)

    if node_id not in _node_buffer:
        _node_buffer[node_id] = {}
    _node_buffer[node_id].update(
        {k: v for k, v in payload.items() if k != "node_id" and v is not None}
    )
    buf = _node_buffer[node_id]

    async with AsyncSessionLocal() as session:
        row = SensorTelemetry(
            timestamp=datetime.utcnow(),
            node_id=node_id,
            temperature=buf.get("temperature"),
            humidity=buf.get("humidity"),
            light_intensity=buf.get("light_intensity"),
        )
        if any(v is not None for v in (row.temperature, row.humidity, row.light_intensity)):
            session.add(row)
        for ev in events:
            session.add(SystemEvent(**ev))
        await session.commit()


def start_subscriber(loop: asyncio.AbstractEventLoop):
    global _loop
    _loop = loop

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if settings.MQTT_USER:
        client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)

    client.on_connect = _on_connect
    client.on_message = _on_message

    client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
    client.loop_forever()
