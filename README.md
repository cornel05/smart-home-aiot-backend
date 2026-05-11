# Smart Home AIoT

Full-stack IoT system — sensor telemetry ingestion, rule-based actuator control, LSTM anomaly prediction, and a React dashboard.

## Architecture

```
YoloBit (serial) ──► Gateway (Python) ──► MQTT Broker (Mosquitto)
                                               │
                                    ┌──────────▼──────────┐
                                    │  Subscriber thread   │
                                    │  (rule engine)       │
                                    └──────────┬──────────┘
                                               │
                          FastAPI backend ◄────┘   ──► TimescaleDB
                               │
                        React dashboard
```

**Data flow:**
1. Gateway reads serial frame (`TEMP:{f},HUM:{f},LIGHT:{f},IR:{i}`) → publishes to 4 Adafruit IO-compatible MQTT feeds
2. Subscriber consumes feeds → runs `rule_engine.evaluate()` → auto-publishes actuator commands → persists `SensorTelemetry` + `SystemEvent`
3. Dashboard polls `/api/sensors/latest` + `/api/sensors/history`; user commands POST to `/api/devices/{device}/command` → manual `SystemEvent` + MQTT actuator packet

**MQTT topics:**

| Direction | Topic | Purpose |
|-----------|-------|---------|
| Inbound | `{AIO_USERNAME}/feeds/smarthome.temperature` | Temperature feed |
| Inbound | `{AIO_USERNAME}/feeds/smarthome.humidity` | Humidity feed |
| Inbound | `{AIO_USERNAME}/feeds/smarthome.light` | Light intensity feed |
| Inbound | `{AIO_USERNAME}/feeds/smarthome.ir-motion` | IR motion feed |
| Outbound | `smarthome/commands` | Actuator commands (JSON) |

**Automation rules** (`services/rule_engine.py`):
- Temperature > 26 °C → `fan on`
- Light intensity < 200 lux → `light on`
- IR > 0 → `ir_motion` event (no actuator)

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI 0.115, SQLAlchemy 2 async |
| Database | TimescaleDB (PostgreSQL 15) via Docker |
| Message broker | Eclipse Mosquitto 2 via Docker |
| AI pipeline | PyTorch 2.4, scikit-learn, pandas |
| Gateway | paho-mqtt 2.1, serial or PTY simulation |
| Frontend | React 19, Vite, Axios, Recharts, Tailwind CSS 4 |

---

## Prerequisites

- Docker + Docker Compose
- Python 3.12+, [uv](https://github.com/astral-sh/uv)
- Node.js 20+

---

## Running the System

### 1 — Infrastructure (DB + MQTT broker)

```bash
docker compose up -d
```

Starts:
- TimescaleDB on `localhost:5432` (auto-runs `database/migrations/001_init.sql`)
- Mosquitto on `localhost:1883` (WebSocket on `localhost:9002`)

Verify:

```bash
docker compose ps        # both services "running"
docker compose logs -f   # watch init logs
```

---

### 2 — Environment

Create `.env` in the project root (all values are optional — defaults work with the Docker setup):

```dotenv
DB_URL=postgresql+asyncpg://smarthome:smarthome@localhost:5432/smarthome
MQTT_HOST=localhost
MQTT_PORT=1883
AIO_USERNAME=your_username   # must match gateway AIO_USERNAME constant
NODE_ID=1
TEMP_FAN_THRESHOLD=26.0
LIGHT_ON_THRESHOLD=200.0
```

---

### 3 — Backend

```bash
uv sync
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

### 4 — Gateway

**Simulation mode** (no hardware — randomised telemetry every 5 s):

```bash
python gateway/gateway.py
```

**Real hardware** (YoloBit over USB serial):

```bash
python gateway/gateway.py --port /dev/ttyUSB0
# or via env var
SERIAL_PORT=/dev/ttyUSB0 python gateway/gateway.py
```

Serial frame format the hardware must emit:

```
TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0
```

---

### 5 — Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

The Vite dev server proxies `/api/*` → `http://localhost:8000`.

---

### Quick dev start (4 terminals)

```bash
# T1 — infra
docker compose up -d

# T2 — backend
uvicorn main:app --reload

# T3 — gateway (simulation)
python gateway/gateway.py

# T4 — frontend
cd frontend && npm run dev
```

---

## API Reference

### Sensors

| Method | Path | Query params | Description |
|--------|------|-------------|-------------|
| GET | `/api/sensors/latest` | `limit=10` (max 100) | Latest N readings |
| GET | `/api/sensors/history` | `minutes=60` (max 1440), `node_id=1` | Readings from last N minutes |

### Devices

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/api/devices/{device}/command` | `{"action": "on"\|"off", "node_id": 1}` | Manual actuator command |
| GET | `/api/devices/events` | `limit=20` | Recent system events |

**Device IDs:** `fan`, `light`, `alarm`

**Example — turn fan on:**

```bash
curl -X POST http://localhost:8000/api/devices/fan/command \
  -H "Content-Type: application/json" \
  -d '{"action": "on"}'
```

---

## Tests

```bash
# Full suite (no DB or broker required — SQLite in-memory)
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov --cov-report=term-missing

# Integration tests only
python -m pytest tests/test_integration_manual_override.py -v
```

| File | Scope |
|------|-------|
| `test_api_devices.py` | Device command + events endpoints |
| `test_api_sensors.py` | Sensor latest/history endpoints |
| `test_rule_engine.py` | Automation threshold logic |
| `test_gateway_serial.py` | Serial frame parsing + PTY I/O |
| `test_architecture_alignment.py` | Model/schema contract |
| `test_integration_manual_override.py` | Full manual override flow (HTTP → MQTT → DB) |

---

## Project Structure

```
.
├── ai/                   # LSTM data pipeline + model
├── api/                  # FastAPI route handlers
├── core/config.py        # Settings (pydantic-settings, reads .env)
├── database/
│   ├── migrations/       # SQL schema (auto-run by Docker on first start)
│   ├── models.py         # SQLAlchemy ORM models
│   └── session.py        # Async engine + get_db dependency
├── frontend/             # React + Vite dashboard
├── gateway/gateway.py    # Sensor simulation / serial reader → MQTT
├── mosquitto/config/     # Mosquitto broker config
├── mqtt/
│   ├── publisher.py      # publish_command(), publish_feed()
│   └── subscriber.py     # Feed consumer + rule engine bridge
├── services/
│   └── rule_engine.py    # Threshold automation rules
├── tests/                # pytest suite
├── docker-compose.yml
├── main.py               # FastAPI app entry point
└── pyproject.toml
```

---

## Configuration Reference

All settings live in `core/config.py` via `pydantic-settings`. Override with env vars or `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_URL` | `postgresql+asyncpg://smarthome:smarthome@localhost:5432/smarthome` | Async DB connection string |
| `MQTT_HOST` | `localhost` | Broker host |
| `MQTT_PORT` | `1883` | Broker port |
| `AIO_USERNAME` | `your_username` | Adafruit IO username (feed topic prefix) |
| `NODE_ID` | `1` | Default sensor node |
| `TEMP_FAN_THRESHOLD` | `26.0` | °C above which fan activates automatically |
| `LIGHT_ON_THRESHOLD` | `200.0` | Lux below which light activates automatically |
