import SensorCard from "./SensorCard";
import Controls from "./Controls";
import AlertBanner from "./AlertBanner";
import LogTable from "./LogTable";

export default function Dashboard({
  current,
  history,
  logs,
  tempThreshold,
  onThresholdChange,
}) {
  const tempAlert = current?.temperature > tempThreshold;
  const humidity = current?.humidity;
  const light = current?.light_intensity;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <span className="eyebrow">Home safety console</span>
          <h1>Smart Home Dashboard</h1>
          <p className="header-copy">
            Warm-room telemetry for temperature, humidity, and ambient light.
          </p>
        </div>
      </header>

      <AlertBanner current={current} tempThreshold={tempThreshold} />

      <div className="section-heading">
        <span className="eyebrow">Environment data stream</span>
        <h2>Live sensor telemetry</h2>
      </div>

      <div className="sensor-grid sensor-grid--three">
        <SensorCard
          title="Temperature"
          dataKey="temperature"
          unit="°C"
          data={history}
          threshold={tempThreshold}
          alert={tempAlert}
        />
        <SensorCard title="Humidity" dataKey="humidity" unit="%" data={history} />
        <SensorCard title="Light Intensity" dataKey="light_intensity" unit=" lux" data={history} />
      </div>

      <div className="dashboard-split">
        <section className="state-panel">
          <div className="section-heading">
            <span className="eyebrow">Environment state</span>
            <h2>Current room status</h2>
          </div>
          <div className="status-list" aria-label="Current home status">
            <div className={`status-badge ${tempAlert ? "status-badge--danger" : "status-badge--safe"}`}>
              <span>DHT11 temp</span>
              <strong>{tempAlert ? "Too warm" : "Comfortable"}</strong>
            </div>
            <div className="status-badge status-badge--neutral">
              <span>Room feel</span>
              <strong>
                {humidity != null && light != null
                  ? `${Math.round(humidity)}% humidity · ${Math.round(light)} lux`
                  : "No reading"}
              </strong>
            </div>
          </div>
        </section>

        <div className="relay-column">
          <div className="section-heading">
            <span className="eyebrow">Relay control panel</span>
            <h2>Gateway commands</h2>
          </div>
          <Controls
            tempThreshold={tempThreshold}
            onThresholdChange={onThresholdChange}
          />
        </div>
      </div>

      <div className="section-heading">
        <span className="eyebrow">Database log view</span>
        <h2>Recent events</h2>
      </div>
      <LogTable logs={logs.slice(0, 5)} />
    </div>
  );
}
