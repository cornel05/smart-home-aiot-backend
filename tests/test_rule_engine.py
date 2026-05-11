import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.rule_engine import evaluate


class TestEvaluateFanRule:
    def test_high_temp_triggers_fan_event(self):
        """temp > 26.0 (TEMP_FAN_THRESHOLD) → fan_activated event returned."""
        with patch("mqtt.publisher.publish_command"):
            events = evaluate({"temperature": 32.0, "node_id": 1})

        assert len(events) == 1
        assert events[0]["event_type"] == "fan_activated"
        assert events[0]["target_device"] == "fan"
        assert events[0]["trigger_source"] == "automatic"
        assert events[0]["value"] == 32.0

    def test_high_temp_calls_publish_command(self):
        """temp > threshold → publish_command('fan', 'on', value=temp) called."""
        with patch("mqtt.publisher.publish_command") as mock_pub:
            evaluate({"temperature": 32.0, "node_id": 1})

        mock_pub.assert_called_once_with("fan", "on", value=32.0)

    def test_temp_at_exact_threshold_no_fan(self):
        """temp == 26.0 is NOT > threshold → no fan event (rule uses strict >)."""
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"temperature": 26.0, "node_id": 1})

        assert events == []
        mock_pub.assert_not_called()

    def test_low_temp_no_fan(self):
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"temperature": 20.0, "node_id": 1})

        assert events == []
        mock_pub.assert_not_called()

    def test_no_temp_key_no_fan(self):
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"humidity": 60.0})

        assert events == []
        mock_pub.assert_not_called()


class TestEvaluateLightRule:
    def test_low_light_triggers_light_event(self):
        """light_intensity < 200.0 → light_activated event returned."""
        with patch("mqtt.publisher.publish_command"):
            events = evaluate({"light_intensity": 150.0, "node_id": 1})

        assert len(events) == 1
        assert events[0]["event_type"] == "light_activated"
        assert events[0]["target_device"] == "light"
        assert events[0]["trigger_source"] == "automatic"
        assert events[0]["value"] == 150.0

    def test_low_light_calls_publish_command(self):
        """light < threshold → publish_command('light', 'on', value=light) called."""
        with patch("mqtt.publisher.publish_command") as mock_pub:
            evaluate({"light_intensity": 150.0, "node_id": 1})

        mock_pub.assert_called_once_with("light", "on", value=150.0)

    def test_light_at_exact_threshold_no_light(self):
        """light == 200.0 is NOT < threshold → no light event (rule uses strict <)."""
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"light_intensity": 200.0, "node_id": 1})

        assert events == []
        mock_pub.assert_not_called()

    def test_bright_light_no_light_command(self):
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"light_intensity": 500.0, "node_id": 1})

        assert events == []
        mock_pub.assert_not_called()

    def test_no_light_key_no_light_command(self):
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"temperature": 20.0})

        assert events == []
        mock_pub.assert_not_called()


class TestEvaluateCombined:
    def test_high_temp_and_low_light_triggers_both(self):
        """Both conditions met → two events, two publish_command calls."""
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"temperature": 32.0, "light_intensity": 150.0, "node_id": 1})

        assert len(events) == 2
        event_types = {e["event_type"] for e in events}
        assert event_types == {"fan_activated", "light_activated"}

        assert mock_pub.call_count == 2
        mock_pub.assert_any_call("fan", "on", value=32.0)
        mock_pub.assert_any_call("light", "on", value=150.0)

    def test_empty_payload_no_events(self):
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({})

        assert events == []
        mock_pub.assert_not_called()

    def test_node_id_defaults_to_settings(self):
        """node_id absent in payload → falls back to settings.NODE_ID (1)."""
        with patch("mqtt.publisher.publish_command"):
            events = evaluate({"temperature": 32.0})

        assert events[0]["node_id"] == 1

    def test_ir_motion_triggers_ir_event(self):
        """ir > 0 → ir_motion event returned (no MQTT publish_command for IR)."""
        with patch("mqtt.publisher.publish_command") as mock_pub:
            events = evaluate({"ir": 1, "node_id": 1})

        assert len(events) == 1
        assert events[0]["event_type"] == "ir_motion"
        assert events[0]["target_device"] == "ir_sensor"
        assert events[0]["trigger_source"] == "automatic"
        assert events[0]["value"] == 1
        mock_pub.assert_not_called()
