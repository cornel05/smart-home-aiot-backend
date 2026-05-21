"""
Tests for gateway serial port reading:
- parse_serial_frame unit tests (pure, no I/O)
- serial_read_thread integration tests using a real pty pair
"""
import os
import pty
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import settings
from gateway.gateway import (
    TOPIC_CMD,
    TOPIC_HUM,
    TOPIC_IR,
    TOPIC_LIGHT,
    TOPIC_TEMP,
    BOARD_DEVICE_IDS,
    BoardSerial,
    handle_command,
    parse_serial_frame,
    serial_read_thread,
    write_board_command,
)


def test_build_board_command_on():
    from gateway.gateway import build_board_command

    assert build_board_command("fan", "on") == "CMD:fan,1\n"


def test_build_board_command_off():
    from gateway.gateway import build_board_command

    assert build_board_command("light", "off") == "CMD:light,0\n"


def test_build_board_command_uses_action_when_value_is_metadata():
    from gateway.gateway import build_board_command

    assert build_board_command("fan", "off", value=1) == "CMD:fan,0\n"


def test_build_board_command_rejects_unknown_action():
    from gateway.gateway import build_board_command

    with pytest.raises(ValueError, match="Unsupported board action"):
        build_board_command("fan", "onn")


def test_build_board_command_rejects_undocumented_action_alias():
    from gateway.gateway import build_board_command

    with pytest.raises(ValueError, match="Unsupported board action"):
        build_board_command("fan", "open")


def test_build_board_command_rejects_protocol_injection_device():
    from gateway.gateway import build_board_command

    with pytest.raises(ValueError, match="Unsupported board device"):
        build_board_command("fan\nCMD:light", "on")


# ---------------------------------------------------------------------------
# Unit tests — parse_serial_frame
# ---------------------------------------------------------------------------


class TestParseSerialFrame:
    def test_valid_frame_returns_correct_dict(self):
        result = parse_serial_frame("TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0")
        assert result == {
            "temperature": 25.3,
            "humidity": 61.5,
            "light_intensity": 430.2,
            "ir": 0.0,
        }

    def test_valid_frame_integer_values(self):
        result = parse_serial_frame("TEMP:22,HUM:55,LIGHT:300,IR:1")
        assert result["temperature"] == 22.0
        assert result["ir"] == 1.0

    def test_negative_temperature_valid(self):
        result = parse_serial_frame("TEMP:-5.0,HUM:80.0,LIGHT:50.0,IR:0")
        assert result["temperature"] == -5.0

    def test_garbage_bytes_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("\xff\x00\x1b[garbage]")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("")

    def test_missing_light_key_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("TEMP:25.3,HUM:61.5,IR:0")

    def test_missing_humidity_key_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("TEMP:25.3,LIGHT:430.2,IR:0")

    def test_extra_field_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0,EXTRA:99")

    def test_partial_frame_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("TEMP:25.3,HUM")

    def test_wrong_key_names_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("temperature:25.3,humidity:61.5,light:430.2,ir:0")

    def test_plain_text_raises(self):
        with pytest.raises(ValueError):
            parse_serial_frame("hello world this is not a sensor")


class TestGatewayConfig:
    def test_topics_come_from_shared_settings(self):
        prefix = f"{settings.AIO_USERNAME}/feeds"

        assert TOPIC_TEMP == f"{prefix}/{settings.MQTT_TOPIC_TEMP}"
        assert TOPIC_HUM == f"{prefix}/{settings.MQTT_TOPIC_HUM}"
        assert TOPIC_LIGHT == f"{prefix}/{settings.MQTT_TOPIC_LIGHT}"
        assert TOPIC_IR == f"{prefix}/{settings.MQTT_TOPIC_IR}"
        assert TOPIC_CMD == settings.MQTT_TOPIC_CMD

    def test_board_device_ids_come_from_actuator_pin_map(self):
        assert BOARD_DEVICE_IDS == set(settings.ACTUATOR_PIN_MAP)


class TestCommandHandling:
    def test_valid_command_payload_returns_command_dict(self):
        result = handle_command(b'{"device":"fan","action":"on","value":32.0}')

        assert result == {"device": "fan", "action": "on", "value": 32.0}

    def test_invalid_command_payload_returns_none(self):
        assert handle_command(b"not json") is None

    def test_write_board_command_without_port_raises(self):
        with pytest.raises(RuntimeError, match="board serial write path"):
            write_board_command("CMD:fan,1\n")

    def test_handle_command_writes_board_command_when_writer_configured(self):
        board_writer = MagicMock()

        result = handle_command(b'{"device":"fan","action":"on"}', board_writer=board_writer)

        assert result == {"device": "fan", "action": "on"}
        board_writer.write.assert_called_once_with(b"CMD:fan,1\n")

    def test_board_serial_reuses_one_open_stream_for_writes(self, tmp_path):
        board_path = tmp_path / "board-serial"
        board_path.touch()
        writer = BoardSerial(str(board_path))
        try:
            write_board_command("CMD:fan,1\n", writer)
            write_board_command("CMD:fan,0\n", writer)
        finally:
            writer.close()

        assert board_path.read_bytes() == b"CMD:fan,1\nCMD:fan,0\n"


# ---------------------------------------------------------------------------
# Helpers for integration tests
# ---------------------------------------------------------------------------


def _make_pty():
    """Return (master_fd, slave_path). Caller owns both fds."""
    master_fd, slave_fd = pty.openpty()
    slave_path = os.ttyname(slave_fd)
    return master_fd, slave_fd, slave_path


def _write(master_fd: int, data: bytes) -> None:
    os.write(master_fd, data)


def _run_thread_until_eof(slave_path: str, client: MagicMock, master_fd: int, delay: float = 0.5):
    """Start serial_read_thread; close master after *delay* seconds to cause EOF."""
    t = threading.Thread(target=serial_read_thread, args=(slave_path, client), daemon=True)
    t.start()
    time.sleep(delay)
    os.close(master_fd)
    t.join(timeout=2.0)


# ---------------------------------------------------------------------------
# Integration tests — serial_read_thread with real pty
# ---------------------------------------------------------------------------


class TestSerialReadThread:
    def test_valid_frame_triggers_four_publishes(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        _write(master_fd, b"TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0\n")
        _run_thread_until_eof(slave_path, client, master_fd)
        os.close(slave_fd)

        assert client.publish.call_count == 4
        calls = {c.args[0]: c.args[1] for c in client.publish.call_args_list}
        assert any("temperature" in k for k in calls)
        assert any("humidity" in k for k in calls)
        assert any("light" in k for k in calls)
        assert any("ir" in k for k in calls)

    def test_garbage_only_no_publish_no_crash(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        garbage = b"\xff\x00\x1b[junk]\xde\xad\xbe\xef\n" * 5
        _write(master_fd, garbage)
        _run_thread_until_eof(slave_path, client, master_fd)
        os.close(slave_fd)

        client.publish.assert_not_called()

    def test_missing_key_frame_no_publish(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        _write(master_fd, b"TEMP:25.3,HUM:61.5,IR:0\n")  # missing LIGHT
        _run_thread_until_eof(slave_path, client, master_fd)
        os.close(slave_fd)

        client.publish.assert_not_called()

    def test_extra_field_frame_no_publish(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        _write(master_fd, b"TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0,EXTRA:99\n")
        _run_thread_until_eof(slave_path, client, master_fd)
        os.close(slave_fd)

        client.publish.assert_not_called()

    def test_mixed_stream_publishes_only_valid_frames(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        _write(master_fd, b"\xff\x00junk\n")                          # garbage
        _write(master_fd, b"TEMP:25.3,HUM:61.5,IR:0\n")              # missing key
        _write(master_fd, b"TEMP:25.3,HUM:61.5,LIGHT:430.2,IR:0\n")  # valid #1
        _write(master_fd, b"hello world\n")                            # plain text
        _write(master_fd, b"TEMP:26.1,HUM:62.0,LIGHT:500.0,IR:1\n")  # valid #2

        _run_thread_until_eof(slave_path, client, master_fd, delay=0.8)
        os.close(slave_fd)

        # 2 valid frames × 4 topics each = 8 publish calls
        assert client.publish.call_count == 8

    def test_fragmented_packet_assembles_correctly(self):
        """Write a valid frame in two chunks; readline should reassemble."""
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        frame = b"TEMP:24.0,HUM:58.0,LIGHT:350.0,IR:0\n"
        split = len(frame) // 2

        t = threading.Thread(target=serial_read_thread, args=(slave_path, client), daemon=True)
        t.start()

        _write(master_fd, frame[:split])
        time.sleep(0.1)
        _write(master_fd, frame[split:])
        time.sleep(0.3)
        os.close(master_fd)
        t.join(timeout=2.0)
        os.close(slave_fd)

        assert client.publish.call_count == 4

    def test_empty_lines_ignored(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        _write(master_fd, b"\n\n\n\n\n")
        _run_thread_until_eof(slave_path, client, master_fd)
        os.close(slave_fd)

        client.publish.assert_not_called()

    def test_bad_port_exits_cleanly(self):
        """Thread exits without exception when port does not exist."""
        client = MagicMock()
        t = threading.Thread(
            target=serial_read_thread, args=("/dev/nonexistent_port_xyz", client), daemon=True
        )
        t.start()
        t.join(timeout=2.0)
        assert not t.is_alive()
        client.publish.assert_not_called()

    def test_negative_temperature_published(self):
        master_fd, slave_fd, slave_path = _make_pty()
        client = MagicMock()

        _write(master_fd, b"TEMP:-3.5,HUM:80.0,LIGHT:50.0,IR:0\n")
        _run_thread_until_eof(slave_path, client, master_fd)
        os.close(slave_fd)

        assert client.publish.call_count == 4
        # Verify temperature value published correctly
        temp_call = next(c for c in client.publish.call_args_list if "temperature" in c.args[0])
        assert temp_call.args[1] == "-3.5"
