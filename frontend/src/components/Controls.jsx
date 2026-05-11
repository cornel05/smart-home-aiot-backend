import { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function sendCommand(device, action) {
  await axios.post(`${API_BASE}/api/devices/${device}/command`, { action });
}

export default function Controls({ tempThreshold, onThresholdChange }) {
  const [fanOn, setFanOn] = useState(false);
  const [alarmReset, setAlarmReset] = useState(false);

  async function toggleFan() {
    const action = fanOn ? "off" : "on";
    await sendCommand("fan", action);
    setFanOn(!fanOn);
  }

  async function resetAlarm() {
    await sendCommand("alarm", "reset");
    setAlarmReset(true);
    setTimeout(() => setAlarmReset(false), 2000);
  }

  return (
    <section className="controls">
      <div className="controls__header">
        <div>
          <span className="eyebrow">Device commands</span>
          <h3>Home response controls</h3>
        </div>
        <small>Commands post to local gateway</small>
      </div>
      <div className="controls-row">
        <button
          className={`ctrl-btn ctrl-btn--fan ${fanOn ? "ctrl-btn--active" : ""}`}
          onClick={toggleFan}
        >
          <span>Fan</span>
          <strong>{fanOn ? "On" : "Off"}</strong>
        </button>
        <button className="ctrl-btn ctrl-btn--danger" onClick={resetAlarm}>
          {alarmReset ? "Alarm Reset" : "Reset Alarm"}
        </button>
      </div>
      <div className="threshold-row">
        <label>
          <span>Temp threshold</span>
          <strong>{tempThreshold}°C</strong>
          <div className="range-wrap">
            <small>20</small>
            <input
              type="range"
              min={20}
              max={40}
              value={tempThreshold}
              onChange={(e) => onThresholdChange("temp", Number(e.target.value))}
            />
            <small>40</small>
          </div>
        </label>
      </div>
    </section>
  );
}
