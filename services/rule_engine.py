from datetime import datetime
from core.config import settings


def evaluate(payload: dict, db_session=None) -> list[dict]:
    """Evaluate sensor payload against rules. Returns list of triggered events."""
    events = []

    temp = payload.get("temperature")
    ir = payload.get("ir")
    light = payload.get("light_intensity")
    node_id = payload.get("node_id", settings.NODE_ID)

    if temp is not None and temp > settings.TEMP_FAN_THRESHOLD:
        from mqtt.publisher import publish_command
        publish_command("fan", "on", value=temp)
        events.append({
            "node_id": node_id,
            "event_type": "fan_activated",
            "trigger_source": "automatic",
            "target_device": "fan",
            "value": temp,
            "timestamp": datetime.utcnow(),
        })

    if light is not None and light < settings.LIGHT_ON_THRESHOLD:
        from mqtt.publisher import publish_command
        publish_command("light", "on", value=light)
        events.append({
            "node_id": node_id,
            "event_type": "light_activated",
            "trigger_source": "automatic",
            "target_device": "light",
            "value": light,
            "timestamp": datetime.utcnow(),
        })

    if ir is not None and ir > 0:
        events.append({
            "node_id": node_id,
            "event_type": "ir_motion",
            "trigger_source": "automatic",
            "target_device": "ir_sensor",
            "value": ir,
            "timestamp": datetime.utcnow(),
        })

    return events
