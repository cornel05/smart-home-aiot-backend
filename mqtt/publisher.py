import json
import paho.mqtt.client as mqtt
from core.config import settings

_client: mqtt.Client | None = None


def get_client() -> mqtt.Client:
    global _client
    if _client is None:
        _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if settings.MQTT_USER:
            _client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
        _client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
        _client.loop_start()
    return _client


def publish_command(device: str, action: str, value: float | None = None) -> None:
    payload = {"device": device, "action": action}
    if value is not None:
        payload["value"] = value
    get_client().publish(settings.MQTT_TOPIC_CMD, json.dumps(payload))
