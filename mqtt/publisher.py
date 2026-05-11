import json
import paho.mqtt.client as mqtt
from core.config import settings

_client: mqtt.Client | None = None

_FEED_KEYS = {
    "temperature": "smarthome.temperature",
    "humidity": "smarthome.humidity",
    "light": "smarthome.light",
    "ir-motion": "smarthome.ir-motion",
}


def adafruit_feed_topic(username: str, feed_key: str) -> str:
    return f"{username}/feeds/{_FEED_KEYS.get(feed_key, feed_key)}"


def configured_feed_topic(feed_key: str) -> str:
    return adafruit_feed_topic(settings.AIO_USERNAME, feed_key)


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


def publish_feed(feed_key: str, value: float | int) -> None:
    get_client().publish(configured_feed_topic(feed_key), str(value))
