import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gateway.gateway import format_serial_frame, parse_serial_frame
from mqtt.publisher import adafruit_feed_topic
from database.models import NodeMetadata, SensorTelemetry, SystemEvent
from ai import data_pipeline


def test_serial_frame_format_is_strict():
    frame = format_serial_frame(temperature=25.5, humidity=61, light=430.2, ir=1)

    assert frame == "TEMP:25.5,HUM:61,LIGHT:430.2,IR:1"
    assert parse_serial_frame(frame) == {
        "temperature": 25.5,
        "humidity": 61.0,
        "light_intensity": 430.2,
        "ir": 1.0,
    }


def test_adafruit_feed_topics_match_standard():
    username = "demo_user"

    assert adafruit_feed_topic(username, "temperature") == "demo_user/feeds/smarthome.temperature"
    assert adafruit_feed_topic(username, "humidity") == "demo_user/feeds/smarthome.humidity"
    assert adafruit_feed_topic(username, "light") == "demo_user/feeds/smarthome.light"
    assert adafruit_feed_topic(username, "ir-motion") == "demo_user/feeds/smarthome.ir-motion"


def test_sensor_telemetry_model_matches_hypertable_columns():
    columns = SensorTelemetry.__table__.columns

    assert set(columns.keys()) == {
        "timestamp",
        "node_id",
        "temperature",
        "humidity",
        "light_intensity",
    }
    assert columns["timestamp"].default is None


def test_system_event_required_columns_match_source_of_truth():
    columns = SystemEvent.__table__.columns

    assert columns["node_id"].nullable is False
    assert columns["event_type"].nullable is False
    assert columns["trigger_source"].nullable is False
    assert columns["target_device"].nullable is False
    assert columns["value"].nullable is True
    assert columns["timestamp"].default is None


def test_node_metadata_matches_source_of_truth():
    columns = NodeMetadata.__table__.columns

    assert columns["location"].type.length == 255
    assert columns["installation_date"].nullable is True
    assert columns["installation_date"].default is None
    assert columns["status"].nullable is True
    assert columns["status"].default is None


def test_ai_features_match_sensor_telemetry_columns():
    assert data_pipeline.FEATURES == ["temperature", "humidity", "light_intensity"]
