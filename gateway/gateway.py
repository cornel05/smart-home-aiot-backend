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
import json
import logging
import os
import random
import re
import sys
import threading
import time
from pathlib import Path

import paho.mqtt.client as mqtt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import settings

MQTT_HOST = settings.MQTT_HOST
MQTT_PORT = settings.MQTT_PORT
MQTT_USER = settings.MQTT_USER
MQTT_PASS = settings.MQTT_PASS
TOPIC_TEMP = f"{settings.AIO_USERNAME}/feeds/{settings.MQTT_TOPIC_TEMP}"
TOPIC_HUM = f"{settings.AIO_USERNAME}/feeds/{settings.MQTT_TOPIC_HUM}"
TOPIC_LIGHT = f"{settings.AIO_USERNAME}/feeds/{settings.MQTT_TOPIC_LIGHT}"
TOPIC_IR = f"{settings.AIO_USERNAME}/feeds/{settings.MQTT_TOPIC_IR}"
TOPIC_CMD = settings.MQTT_TOPIC_CMD
BOARD_DEVICE_IDS = set(settings.ACTUATOR_PIN_MAP)
BOARD_ON_ACTIONS = {"on"}
BOARD_OFF_ACTIONS = {"off"}
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


def build_board_command(device: str, action: str, value: int | None = None) -> str:
    if device not in BOARD_DEVICE_IDS:
        raise ValueError(f"Unsupported board device: {device}")

    normalized_action = action.lower()
    if normalized_action in BOARD_ON_ACTIONS:
        state = 1
    elif normalized_action in BOARD_OFF_ACTIONS:
        state = 0
    else:
        raise ValueError(f"Unsupported board action: {action}")

    return f"CMD:{device},{state}\n"


class BoardSerial:
    def __init__(self, port: str):
        self.port = port
        self._stream = open(port, "r+b", buffering=0)  # noqa: SIM115 - closed by close()
        self._write_lock = threading.Lock()

    def readline(self) -> bytes:
        return self._stream.readline()

    def write(self, data: bytes) -> None:
        with self._write_lock:
            self._stream.write(data)
            try:
                self._stream.flush()
            except AttributeError:
                pass

    def close(self) -> None:
        self._stream.close()


def write_board_command(command: str, board_writer=None) -> None:
    if board_writer is None:
        raise RuntimeError("board serial write path is not configured")
    board_writer.write(command.encode("utf-8"))


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


def serial_read_thread(port: str, client: mqtt.Client, board_serial: BoardSerial | None = None) -> None:
    """Read serial frames from *port*, publish valid ones, silently discard garbage."""
    logger.info("Opening serial port %s", port)
    owns_serial = board_serial is None
    if board_serial is None:
        try:
            ser = open(port, "rb", buffering=0)  # noqa: SIM115 — manual close below
        except OSError as exc:
            logger.error("Cannot open serial port %s: %s", port, exc)
            return
    else:
        ser = board_serial

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
        if owns_serial:
            ser.close()


def handle_command(raw_payload: bytes | str, board_writer=None) -> dict | None:
    """Parse actuator command payload; future YoloBit adapter should dispatch here."""
    try:
        if isinstance(raw_payload, bytes):
            raw_payload = raw_payload.decode("utf-8")
        payload = json.loads(raw_payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        logger.warning("Bad command payload (discarded): %r (%s)", raw_payload, exc)
        return None

    if not isinstance(payload, dict) or "device" not in payload or "action" not in payload:
        logger.warning("Bad command payload (discarded): %r", payload)
        return None

    command = {
        "device": str(payload["device"]),
        "action": str(payload["action"]),
    }
    if "value" in payload:
        command["value"] = payload["value"]

    logger.info("CMD ← %s", command)
    if board_writer is not None:
        board_command = build_board_command(
            command["device"], command["action"], command.get("value")
        )
        write_board_command(board_command, board_writer)
    return command


def command_subscriber_thread(board_writer=None) -> None:
    """Subscribe to smarthome/commands and log actuator commands from the backend."""

    def on_connect(c, userdata, flags, reason_code, properties):
        if reason_code == 0:
            c.subscribe(TOPIC_CMD)
            logger.info("Command subscriber connected, subscribed to %s", TOPIC_CMD)
        else:
            logger.error("Command subscriber connect failed: %s", reason_code)

    def on_message(c, userdata, msg):
        try:
            handle_command(msg.payload, board_writer=board_writer)
        except Exception as exc:
            logger.error("Board command write failed: %s", exc)

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

    board_serial = None
    if args.port:
        try:
            board_serial = BoardSerial(args.port)
        except OSError as exc:
            logger.error("Cannot open serial port %s: %s", args.port, exc)
            return
        data_thread = threading.Thread(
            target=serial_read_thread,
            args=(args.port, client, board_serial),
            name="SerialRead",
            daemon=True,
        )
        logger.info("Serial mode — reading from %s", args.port)
    else:
        data_thread = threading.Thread(
            target=telemetry_thread, args=(client,), name="Telemetry", daemon=True
        )
        logger.info("Simulation mode — generating internal frames")

    threads = [
        data_thread,
        threading.Thread(
            target=command_subscriber_thread,
            args=(board_serial,),
            name="CmdSub",
            daemon=True,
        ),
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
