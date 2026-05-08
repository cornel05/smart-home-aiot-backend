-- TimescaleDB initialization for Smart Home AIoT
-- Run against a PostgreSQL + TimescaleDB instance

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Table 1: Node Metadata
CREATE TABLE IF NOT EXISTS node_metadata (
    node_id          SERIAL PRIMARY KEY,
    location         VARCHAR(100),
    installation_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status           VARCHAR(50) NOT NULL DEFAULT 'active'
);

-- Seed default node
INSERT INTO node_metadata (location, status)
VALUES ('Living Room', 'active')
ON CONFLICT DO NOTHING;

-- Table 2: Sensor Telemetry (hypertable)
CREATE TABLE IF NOT EXISTS sensor_telemetry (
    "timestamp"     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    node_id         INTEGER NOT NULL REFERENCES node_metadata(node_id),
    temperature     DOUBLE PRECISION,
    humidity        DOUBLE PRECISION,
    light_intensity DOUBLE PRECISION,
    gas_ppm         DOUBLE PRECISION,
    door_open       BOOLEAN,
    PRIMARY KEY ("timestamp", node_id)
);

SELECT create_hypertable(
    'sensor_telemetry',
    'timestamp',
    if_not_exists => TRUE
);

-- Compress chunks older than 7 days
ALTER TABLE sensor_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('sensor_telemetry', INTERVAL '7 days', if_not_exists => TRUE);

-- Table 3: System Events
CREATE TABLE IF NOT EXISTS system_events (
    event_id       SERIAL PRIMARY KEY,
    "timestamp"    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    node_id        INTEGER REFERENCES node_metadata(node_id),
    event_type     VARCHAR(100) NOT NULL,
    trigger_source VARCHAR(50) NOT NULL DEFAULT 'automatic',
    target_device  VARCHAR(100),
    value          DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON system_events ("timestamp" DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON system_events (event_type);
