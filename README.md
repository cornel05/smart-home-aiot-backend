# Smart Home AIoT — Setup Guide

## Prerequisites

- Docker + Docker Compose
- Python 3.12+, [uv](https://github.com/astral-sh/uv)
- Node.js 20+
- VS Code + the stable **Pymakr** extension by Pycom for Yolo:Bit firmware upload
- Yolo:Bit running MicroPython, USB cable with data support, and Linux serial access to `/dev/ttyUSB*` or `/dev/ttyACM*`

On Linux, if the board appears but Pymakr or the gateway cannot open it, add your user to the serial group and reconnect:

```bash
sudo usermod -aG dialout "$USER"
newgrp dialout
```

---

## 1 — Infrastructure (DB + MQTT broker)

```bash
docker compose up -d
```

Starts:
- TimescaleDB on `localhost:5432`
- Mosquitto on `localhost:1883` (WebSocket on `localhost:9002`)

Verify:

```bash
docker compose ps
docker compose logs -f
```

---

## 2 — Environment

Create `.env` in the project root:

```dotenv
DB_URL=postgresql+asyncpg://smarthome:smarthome@localhost:5432/smarthome
MQTT_HOST=localhost
MQTT_PORT=1883
AIO_USERNAME=your_username   # shared by backend and gateway topic builders
NODE_ID=1
TEMP_FAN_THRESHOLD=26.0
LIGHT_ON_THRESHOLD=200.0
ACTUATOR_PIN_MAP='{"fan":10,"light":13}'
```

All values optional — defaults work with the Docker setup.

---

## 3 — Yolo:Bit Firmware Upload With Pymakr

The board firmware lives in `firmware/yolobit/`. It emits sensor frames over serial and accepts actuator commands from the gateway.

Board serial output:

```text
TEMP:25.3,HUM:61.5,LIGHT:430,IR:0
```

Board command input:

```text
CMD:{device},{state}
```

Default actuator mapping:

| Device | Yolo:Bit pin | Output call |
|--------|--------------|-------------|
| `fan` | pin 10 | `yolobit.pin10.write_digital(0\|1)` |
| `light` | pin 13 | `yolobit.pin13.write_digital(0\|1)` |

Confirm real relay wiring before powering motors or external loads.

### Install the correct Pymakr extension

1. Open VS Code.
2. Open Extensions.
3. Search `Pymakr`.
4. Install **Pymakr** by **Pycom**.
5. Do not install **Pymakr - Preview**. If Preview is installed, uninstall it first.

### Open the firmware workspace

Use the firmware workspace file, not the repo root:

```text
firmware/yolobit/yolobit.code-workspace
```

In VS Code:

1. `File` → `Open Workspace from File...`
2. Select `firmware/yolobit/yolobit.code-workspace`
3. Trust the workspace if VS Code asks.

This workspace uses `firmware/yolobit/pymakr.conf`, so Pymakr uploads only board firmware files, not backend/frontend/test code.

### Connect and upload

1. Plug in the Yolo:Bit.
2. In the Pymakr panel, choose **Add device**.
3. Select the serial device:
   - Linux: usually `/dev/ttyUSB0` or `/dev/ttyACM0`
   - macOS: usually `/dev/cu.usbserial-*` or `/dev/cu.usbmodem*`
   - Windows: usually `COM3`, `COM4`, etc.
4. Click **Connect device**.
5. Open a Pymakr terminal or REPL.
6. Stop any running script with `Ctrl+C`.
7. Click **Sync project to device**.
8. Soft reset the board from Pymakr, or press `Ctrl+D` in the REPL.

Files expected on the Yolo:Bit root filesystem:

```text
main.py
dht20.py
lcd_1602.py
task_actuators.py
```

### Verify firmware

After reset, the Pymakr terminal should show an I2C scan and sensor frames:

```text
I2C_SCAN:[56, ...]
TEMP:25.3,HUM:61.5,LIGHT:430,IR:0
```

`56` is DHT20 (`0x38`). LCD addresses are commonly `33` (`0x21`), `39` (`0x27`), or `63` (`0x3f`). If the LCD does not initialize, edit `LCD_ADDR` in `firmware/yolobit/main.py`.

Manual actuator check from the REPL:

```python
import task_actuators
task_actuators.task_init()
task_actuators.set_device("fan", 1)
task_actuators.set_device("fan", 0)
task_actuators.set_device("light", 1)
task_actuators.set_device("light", 0)
```

Expected logs:

```text
[ACTUATOR] fan=1
[ACTUATOR] fan=0
[ACTUATOR] light=1
[ACTUATOR] light=0
```

### Firmware pin troubleshooting

The firmware defaults to `SoftI2C(scl=Pin(22), sda=Pin(21))`. If `I2C_SCAN:[]` appears, try these pairs in `firmware/yolobit/main.py`:

```python
I2C_SCL_PIN = 19
I2C_SDA_PIN = 20
```

If still empty, try swapped pairs:

```python
I2C_SCL_PIN = 20
I2C_SDA_PIN = 19
```

```python
I2C_SCL_PIN = 21
I2C_SDA_PIN = 22
```

---

## 4 — Backend

**Linux / macOS:**

```bash
uv sync
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Windows:**

```bash
uv sync
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## 5 — Gateway

**Simulation mode** (no hardware):

```bash
python gateway/gateway.py
```

**Real hardware (Yolo:Bit over USB serial):**

Linux:

```bash
python gateway/gateway.py --port /dev/ttyUSB0
# or
SERIAL_PORT=/dev/ttyUSB0 python gateway/gateway.py
```

macOS:

```bash
python gateway/gateway.py --port /dev/cu.usbserial-0001
```

Windows:

```bash
python gateway/gateway.py --port COM3
# or
set SERIAL_PORT=COM3 && python gateway/gateway.py
```

Use the same serial path selected in Pymakr. Stop the Pymakr terminal before running the gateway if the OS allows only one serial owner.

Serial frame format the hardware must emit:

```
TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0
```

When `--port` is set, gateway commands are written back to the same Yolo:Bit serial path:

```
CMD:{device},{state}
```

---

## 6 — Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

The Vite dev server proxies `/api/*` → `http://localhost:8000`.

---

## Quick Dev Start (4 terminals)

```bash
# T1 — infra
docker compose up -d

# T2 — backend
uvicorn main:app --reload

# T3 — gateway (simulation)
python gateway/gateway.py

# T3 hardware alternative, after Pymakr upload/reset
python gateway/gateway.py --port /dev/ttyUSB0

# T4 — frontend
cd frontend && npm run dev
```

---

## Configuration Reference

All settings in `core/config.py` via `pydantic-settings`. Override with env vars or `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_URL` | `postgresql+asyncpg://smarthome:smarthome@localhost:5432/smarthome` | Async DB connection string |
| `MQTT_HOST` | `localhost` | Broker host |
| `MQTT_PORT` | `1883` | Broker port |
| `AIO_USERNAME` | `your_username` | Adafruit IO username (feed topic prefix) |
| `NODE_ID` | `1` | Default sensor node |
| `TEMP_FAN_THRESHOLD` | `26.0` | °C above which fan activates automatically |
| `LIGHT_ON_THRESHOLD` | `200.0` | Lux below which light activates automatically |
| `ACTUATOR_PIN_MAP` | `{"fan":10,"light":13}` | Yolo:Bit GPIO pin assignments |
