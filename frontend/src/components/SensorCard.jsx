import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function SensorCard({ title, dataKey, unit, data, alert = false }) {
  const chartData = data.map((row) => ({
    time: new Date(row.timestamp).toLocaleTimeString(),
    value: row[dataKey],
  }));

  const current = chartData.at(-1)?.value;

  return (
    <div className={`sensor-card ${alert ? "sensor-card--alert" : ""}`}>
      <h3>{title}</h3>
      <p className="sensor-value">
        {current != null ? `${current}${unit}` : "—"}
      </p>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={chartData}>
          <XAxis dataKey="time" hide />
          <YAxis hide />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="value"
            stroke={alert ? "#ef4444" : "#6366f1"}
            dot={false}
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
