import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const SENSOR_META = {
  temperature: { label: "Comfort band", accent: "#c45f38", soft: "#f8d7c8" },
  humidity: { label: "Air moisture", accent: "#477a8f", soft: "#cfe7ef" },
  light_intensity: { label: "Ambient light", accent: "#b9892d", soft: "#f4dfae" },
};

function formatValue(value, unit) {
  if (value == null) return "No data";
  const rounded = Number.isInteger(value) ? value : Number(value).toFixed(1);
  return `${rounded}${unit}`;
}

export default function SensorCard({ title, dataKey, unit, data, threshold, alert = false }) {
  const chartData = data.map((row) => ({
    time: new Date(row.timestamp).toLocaleTimeString(),
    value: row[dataKey],
  }));

  const current = chartData.at(-1)?.value;
  const previous = chartData.at(-2)?.value;
  const delta = current != null && previous != null ? current - previous : null;
  const meta = SENSOR_META[dataKey] || SENSOR_META.temperature;
  const tone = alert ? "#b42318" : meta.accent;

  return (
    <article
      className={`sensor-card ${alert ? "sensor-card--alert" : ""}`}
      style={{ "--sensor": tone, "--sensor-soft": meta.soft }}
    >
      <div className="sensor-card__top">
        <div>
          <span>{meta.label}</span>
          <h3>{title}</h3>
        </div>
        <small>{alert ? "Alert" : "Live"}</small>
      </div>

      <p className="sensor-value">{formatValue(current, unit)}</p>
      <div className="sensor-meta">
        <span>
          {delta == null
            ? "Awaiting trend"
            : `${delta >= 0 ? "+" : ""}${delta.toFixed(1)} since last read`}
        </span>
        {threshold != null && <span>Limit {threshold}{unit}</span>}
      </div>

      <div className="chart-shell">
        {chartData.length > 1 ? (
          <ResponsiveContainer width="100%" height={116}>
            <LineChart data={chartData} margin={{ top: 10, right: 4, bottom: 0, left: 4 }}>
              <XAxis dataKey="time" hide />
              <YAxis hide domain={["dataMin", "dataMax"]} />
              <Tooltip
                cursor={{ stroke: "rgba(94, 57, 38, 0.16)", strokeWidth: 1 }}
                contentStyle={{
                  background: "#fffaf3",
                  border: "1px solid #ead8c4",
                  borderRadius: 10,
                  color: "#3b2a20",
                  boxShadow: "0 18px 45px rgba(72, 45, 28, 0.18)",
                }}
                formatter={(value) => [formatValue(value, unit), title]}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={tone}
                dot={false}
                strokeWidth={3}
                activeDot={{ r: 5, strokeWidth: 0, fill: tone }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-empty">Waiting for sensor history</div>
        )}
      </div>
    </article>
  );
}
