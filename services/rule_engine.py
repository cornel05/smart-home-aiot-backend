from datetime import datetime
from core.config import settings


def evaluate(payload: dict, db_session=None) -> list[dict]:
    """Evaluate sensor payload against rules. Returns list of triggered events."""
    events = []

    temp = payload.get("temperature")
    gas_ppm = payload.get("gas_ppm")
    door_open = payload.get("door_open")
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

    if gas_ppm is not None and gas_ppm > settings.GAS_ALERT_THRESHOLD:
        from mqtt.publisher import publish_command
        publish_command("alarm", "trigger", value=gas_ppm)
        events.append({
            "node_id": node_id,
            "event_type": "gas_alert",
            "trigger_source": "automatic",
            "target_device": "alarm",
            "value": gas_ppm,
            "timestamp": datetime.utcnow(),
        })

    if door_open is True:
        events.append({
            "node_id": node_id,
            "event_type": "door_opened",
            "trigger_source": "automatic",
            "target_device": None,
            "value": None,
            "timestamp": datetime.utcnow(),
        })

    return events
