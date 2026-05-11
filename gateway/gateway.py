"""
Laptop-based IoT gateway.
Simulates the report-defined serial frame and publishes each value to
Adafruit IO compatible MQTT feed topics.
Also runs a command subscriber thread that receives actuator commands
from the backend (smarthome/commands) and logs them.

Physical swap guide (per thread):
  DHT11  → dht.DHT11(machine.Pin(N)).measure(); .temperature(); .humidity()
  IR     → machine.Pin(N, machine.Pin.IN).value()
  BH1750 → I2C(0, scl=Pin(22), sda=Pin(21)).readfrom(0x23, 2); parse lux

Serial port mode (real hardware / virtual pty):
  SERIAL_PORT=/dev/ttyUSB0 python gateway/gateway.py
  -- or --
  python gateway/gateway.py --port /dev/ttyUSB0
"""
import argparse
import logging
import os
import random
import re
import threading
import time

import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASS = ""
AIO_USERNAME = "your_username"
TOPIC_TEMP = f"{AIO_USERNAME}/feeds/smarthome.temperature"
TOPIC_HUM = f"{AIO_USERNAME}/feeds/smarthome.humidity"
TOPIC_LIGHT = f"{AIO_USERNAME}/feeds/smarthome.light"
TOPIC_IR = f"{AIO_USERNAME}/feeds/smarthome.ir-motion"
TOPIC_CMD = "smarthome/commands"
SERIAL_FRAME_RE = re.compile(
    r"^TEMP:(?P<temperature>-?\d+(?:\.\d+)?),"
    r"HUM:(?P<humidity>-?\d+(?:\.\d+)?),"
    r"LIGHT:(?P<light_intensity>-?\d+(?:\.\d+)?),"
    r"IR:(?P<ir>-?\d+(?:\.\d+)?)$"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(threadName)s] %(message)s")
logger = logging.getLogger(__name__)


def format_serial_frame(temperature: float, humidity: float, light: float, ir: int) -> str:
    return f"TEMP:{temperature},HUM:{humidity},LIGHT:{light},IR:{ir}"


def parse_serial_frame(frame: str) -> dict[str, float]:
    match = SERIAL_FRAME_RE.fullmatch(frame)
    if not match:
        raise ValueError("Serial frame must match TEMP:{},HUM:{},LIGHT:{},IR:{}")
    return {key: float(value) for key, value in match.groupdict().items()}


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


def telemetry_thread(client: mqtt.Client) -> None:
    """Simulate one strict serial frame every 5 seconds."""
    base_temp = 24.0
    base_hum = 60.0
    while True:
        temperature = round(base_temp + random.uniform(-2, 4), 1)
        humidity = round(base_hum + random.uniform(-10, 10), 1)
        if random.random() < 0.05:
            lux = round(random.uniform(1, 50), 1)
        else:
            lux = round(random.uniform(100, 800), 1)
        ir = 1 if random.random() < 0.1 else 0
        frame = format_serial_frame(temperature, humidity, lux, ir)
        values = parse_serial_frame(frame)

        client.publish(TOPIC_TEMP, str(values["temperature"]))
        client.publish(TOPIC_HUM, str(values["humidity"]))
        client.publish(TOPIC_LIGHT, str(values["light_intensity"]))
        client.publish(TOPIC_IR, str(int(values["ir"])))
        logger.info("Serial → %s", frame)
        time.sleep(5)


def serial_read_thread(port: str, client: mqtt.Client) -> None:
    """Read serial frames from *port*, publish valid ones, silently discard garbage."""
    logger.info("Opening serial port %s", port)
    try:
        ser = open(port, "rb", buffering=0)  # noqa: SIM115 — manual close below
    except OSError as exc:
        logger.error("Cannot open serial port %s: %s", port, exc)
        return

    try:
        while True:
            try:
                raw = ser.readline()
            except OSError as exc:
                logger.error("Serial read error on %s: %s", port, exc)
                break

            if not raw:
                continue

            frame = raw.decode("utf-8", errors="replace").strip()
            if not frame:
                continue

            try:
                values = parse_serial_frame(frame)
            except ValueError:
                logger.warning("Bad frame (discarded): %r", frame)
                continue

            client.publish(TOPIC_TEMP, str(values["temperature"]))
            client.publish(TOPIC_HUM, str(values["humidity"]))
            client.publish(TOPIC_LIGHT, str(values["light_intensity"]))
            client.publish(TOPIC_IR, str(int(values["ir"])))
            logger.info("Serial → %s", frame)
    finally:
        ser.close()


def command_subscriber_thread() -> None:
    """Subscribe to smarthome/commands and log actuator commands from the backend."""

    def on_connect(c, userdata, flags, reason_code, properties):
        if reason_code == 0:
            c.subscribe(TOPIC_CMD)
            logger.info("Command subscriber connected, subscribed to %s", TOPIC_CMD)
        else:
            logger.error("Command subscriber connect failed: %s", reason_code)

    def on_message(c, userdata, msg):
        logger.info("CMD ← %s", msg.payload.decode())

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()


def main():
    parser = argparse.ArgumentParser(description="IoT Gateway")
    parser.add_argument(
        "--port",
        default=os.environ.get("SERIAL_PORT"),
        help="Serial/pty port to read from (omit to use internal simulation)",
    )
    args = parser.parse_args()

    client = make_client()
    time.sleep(1)

    if args.port:
        data_thread = threading.Thread(
            target=serial_read_thread, args=(args.port, client), name="SerialRead", daemon=True
        )
        logger.info("Serial mode — reading from %s", args.port)
    else:
        data_thread = threading.Thread(
            target=telemetry_thread, args=(client,), name="Telemetry", daemon=True
        )
        logger.info("Simulation mode — generating internal frames")

    threads = [
        data_thread,
        threading.Thread(target=command_subscriber_thread, name="CmdSub", daemon=True),
    ]
    for t in threads:
        t.start()

    logger.info("Gateway running — Ctrl+C to stop.")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        logger.info("Gateway stopped.")


if __name__ == "__main__":
    main()
