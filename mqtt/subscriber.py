import json
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
        client.subscribe(settings.MQTT_TOPIC_SENSOR)
        logger.info("MQTT subscriber connected, subscribed to %s", settings.MQTT_TOPIC_SENSOR)
    else:
        logger.error("MQTT connect failed: %s", reason_code)


_SENSOR_FIELDS = {"temperature", "humidity", "light_intensity", "gas_ppm", "door_open"}

# Fields that are mutually exclusive per physical sensor type.
_EXCLUSIVE_GROUPS = [
    {"temperature", "humidity"},   # DHT11
    {"gas_ppm"},                   # MQ-2
    {"door_open"},                 # Reed
    {"light_intensity"},           # BH1750
]


def _validate_payload(payload: dict) -> bool:
    if "node_id" not in payload:
        logger.warning("Dropping payload missing node_id: %s", payload)
        return False
    present = _SENSOR_FIELDS & payload.keys()
    if not present:
        logger.warning("Dropping payload with no recognized sensor fields: %s", payload)
        return False
    # Warn when fields from physically separate sensors coexist in one message.
    groups_present = [g for g in _EXCLUSIVE_GROUPS if g & present]
    if len(groups_present) > 1:
        logger.warning(
            "Payload contains fields from %d sensor types — possible schema violation: %s",
            len(groups_present),
            payload,
        )
    return True


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        logger.info("Received: %s", payload)

        if not _validate_payload(payload):
            return

        events = evaluate(payload)

        if _loop and not _loop.is_closed():
            asyncio.run_coroutine_threadsafe(_persist(payload, events), _loop)
    except Exception as exc:
        logger.exception("Error processing MQTT message: %s", exc)


async def _persist(payload: dict, events: list[dict]):
    from database.session import AsyncSessionLocal
    from database.models import SensorTelemetry, SystemEvent
    from core.config import settings as cfg

    async with AsyncSessionLocal() as session:
        row = SensorTelemetry(
            timestamp=datetime.utcnow(),
            node_id=payload.get("node_id", cfg.NODE_ID),
            temperature=payload.get("temperature"),
            humidity=payload.get("humidity"),
            light_intensity=payload.get("light_intensity"),
            gas_ppm=payload.get("gas_ppm"),
            door_open=payload.get("door_open"),
        )
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
