"""
Laptop-based IoT gateway.
Simulates four sensor types via daemon threads:
  - DHT11  : temperature + humidity every 5 s
  - MQ-2   : gas PPM every 5 s, random spike to trigger alerts
  - Reed   : door open/close toggle every 10 s
  - BH1750 : light intensity (lux) every 5 s
Also runs a command subscriber thread that receives actuator commands
from the backend (smarthome/commands) and logs them.
All sensor threads publish JSON to MQTT broker running on localhost.

Physical swap guide (per thread):
  DHT11  → dht.DHT11(machine.Pin(N)).measure(); .temperature(); .humidity()
  MQ-2   → machine.ADC(machine.Pin(N)).read_u16() + voltage-to-ppm curve
  Reed   → machine.Pin(N, machine.Pin.IN, machine.Pin.PULL_UP).value()
  BH1750 → I2C(0, scl=Pin(22), sda=Pin(21)).readfrom(0x23, 2); parse lux
"""
import json
import logging
import random
import threading
import time

import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASS = ""
TOPIC_SENSOR = "smarthome/sensors"
TOPIC_CMD = "smarthome/commands"
NODE_ID = 1
GAS_ALERT_THRESHOLD = 300.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s] %(message)s")
logger = logging.getLogger(__name__)


def make_client() -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    def on_connect(c, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info("Connected to broker %s:%s", MQTT_HOST, MQTT_PORT)
        else:
            logger.error("Broker connect failed: %s", reason_code)

    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    return client


def dht11_thread(client: mqtt.Client) -> None:
    """Simulate DHT11: temperature 20–35°C, humidity 40–90%."""
    base_temp = 24.0
    base_hum = 60.0
    while True:
        temperature = round(base_temp + random.uniform(-2, 4), 1)
        humidity = round(base_hum + random.uniform(-10, 10), 1)
        payload = {
            "node_id": NODE_ID,
            "sensor": "dht11",
            "temperature": temperature,
            "humidity": humidity,
        }
        client.publish(TOPIC_SENSOR, json.dumps(payload))
        logger.info("DHT11 → temp=%.1f°C hum=%.1f%%", temperature, humidity)
        time.sleep(5)


def mq2_thread(client: mqtt.Client) -> None:
    """Simulate MQ-2 gas sensor: normal 50–200 ppm, rare spike 300–600 ppm."""
    while True:
        if random.random() < 0.1:
            gas_ppm = round(random.uniform(310, 600), 1)
        else:
            gas_ppm = round(random.uniform(50, 200), 1)
        alert = gas_ppm > GAS_ALERT_THRESHOLD
        payload = {
            "node_id": NODE_ID,
            "sensor": "mq2",
            "gas_ppm": gas_ppm,
            "alert": alert,
        }
        client.publish(TOPIC_SENSOR, json.dumps(payload))
        logger.info("MQ-2  → gas=%.1f ppm alert=%s", gas_ppm, alert)
        time.sleep(5)


def reed_thread(client: mqtt.Client) -> None:
    """Simulate Reed Switch: toggle door_open state every 10 s."""
    door_open = False
    while True:
        time.sleep(10)
        door_open = not door_open
        payload = {
            "node_id": NODE_ID,
            "sensor": "reed",
            "door_open": door_open,
        }
        client.publish(TOPIC_SENSOR, json.dumps(payload))
        logger.info("Reed  → door_open=%s", door_open)


def bh1750_thread(client: mqtt.Client) -> None:
    """Simulate BH1750 light sensor: normal 100–800 lux, rare low-light < 50 lux."""
    while True:
        if random.random() < 0.05:
            lux = round(random.uniform(1, 50), 1)
        else:
            lux = round(random.uniform(100, 800), 1)
        payload = {
            "node_id": NODE_ID,
            "sensor": "bh1750",
            "light_intensity": lux,
        }
        client.publish(TOPIC_SENSOR, json.dumps(payload))
        logger.info("BH1750 → lux=%.1f", lux)
        time.sleep(5)


def command_subscriber_thread() -> None:
    """Subscribe to smarthome/commands and log actuator commands from the backend."""

    def on_connect(c, userdata, flags, reason_code, properties):
        if reason_code == 0:
            c.subscribe(TOPIC_CMD)
            logger.info("Command subscriber connected, subscribed to %s", TOPIC_CMD)
        else:
            logger.error("Command subscriber connect failed: %s", reason_code)

    def on_message(c, userdata, msg):
        try:
            cmd = json.loads(msg.payload.decode())
            logger.info(
                "CMD ← device=%s action=%s value=%s",
                cmd.get("device"),
                cmd.get("action"),
                cmd.get("value"),
            )
        except Exception as exc:
            logger.exception("Failed to parse command: %s", exc)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


def main():
    client = make_client()
    time.sleep(1)

    threads = [
        threading.Thread(target=dht11_thread, args=(client,), name="DHT11", daemon=True),
        threading.Thread(target=mq2_thread, args=(client,), name="MQ-2", daemon=True),
        threading.Thread(target=reed_thread, args=(client,), name="Reed", daemon=True),
        threading.Thread(target=bh1750_thread, args=(client,), name="BH1750", daemon=True),
        threading.Thread(target=command_subscriber_thread, name="CmdSub", daemon=True),
    ]
    for t in threads:
        t.start()

    logger.info("Gateway running — 4 sensor threads + command subscriber active. Ctrl+C to stop.")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        logger.info("Gateway stopped.")


if __name__ == "__main__":
    main()
