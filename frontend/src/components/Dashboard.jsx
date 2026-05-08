import { useState } from "react";
import { useSensorData } from "../hooks/useSensorData";
import SensorCard from "./SensorCard";
import Controls from "./Controls";
import AlertBanner from "./AlertBanner";

export default function Dashboard() {
  const { current, history, error } = useSensorData(5000);
  const [gasThreshold, setGasThreshold] = useState(300);
  const [tempThreshold, setTempThreshold] = useState(26);

  function handleThreshold(type, value) {
    if (type === "gas") setGasThreshold(value);
    if (type === "temp") setTempThreshold(value);
  }

  const gasAlert = current?.gas_ppm > gasThreshold;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Smart Home Dashboard</h1>
        {error && <span className="connection-error">Backend offline: {error}</span>}
        {current && (
          <span className="last-update">
            Updated: {new Date(current.timestamp).toLocaleTimeString()}
          </span>
        )}
      </header>

      <AlertBanner current={current} gasThreshold={gasThreshold} />

      <div className="status-row">
        <div className={`status-badge ${current?.door_open ? "status-badge--open" : "status-badge--closed"}`}>
          Door: {current?.door_open ? "Open" : "Closed"}
        </div>
        <div className={`status-badge ${gasAlert ? "status-badge--danger" : "status-badge--safe"}`}>
          Gas: {gasAlert ? "ALERT" : "Normal"}
        </div>
      </div>

      <div className="sensor-grid">
        <SensorCard
          title="Temperature"
          dataKey="temperature"
          unit="°C"
          data={history}
          alert={current?.temperature > tempThreshold}
        />
        <SensorCard
          title="Humidity"
          dataKey="humidity"
          unit="%"
          data={history}
        />
        <SensorCard
          title="Light Intensity"
          dataKey="light_intensity"
          unit=" lux"
          data={history}
        />
        <SensorCard
          title="Gas (MQ-2)"
          dataKey="gas_ppm"
          unit=" ppm"
          data={history}
          alert={gasAlert}
        />
      </div>

      <Controls
        gasThreshold={gasThreshold}
        tempThreshold={tempThreshold}
        onThresholdChange={handleThreshold}
      />
    </div>
  );
}
