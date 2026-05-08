import { useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function sendCommand(device, action) {
  await axios.post(`${API_BASE}/api/devices/${device}/command`, { action });
}

export default function Controls({ gasThreshold, tempThreshold, onThresholdChange }) {
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
    <div className="controls">
      <h3>Controls</h3>
      <div className="controls-row">
        <button
          className={`ctrl-btn ${fanOn ? "ctrl-btn--active" : ""}`}
          onClick={toggleFan}
        >
          Fan {fanOn ? "ON" : "OFF"}
        </button>
        <button className="ctrl-btn ctrl-btn--danger" onClick={resetAlarm}>
          {alarmReset ? "Alarm Reset" : "Reset Alarm"}
        </button>
      </div>
      <div className="threshold-row">
        <label>
          Temp threshold (°C): <strong>{tempThreshold}</strong>
          <input
            type="range"
            min={20}
            max={40}
            value={tempThreshold}
            onChange={(e) => onThresholdChange("temp", Number(e.target.value))}
          />
        </label>
        <label>
          Gas threshold (ppm): <strong>{gasThreshold}</strong>
          <input
            type="range"
            min={100}
            max={600}
            step={10}
            value={gasThreshold}
            onChange={(e) => onThresholdChange("gas", Number(e.target.value))}
          />
        </label>
      </div>
    </div>
  );
}
