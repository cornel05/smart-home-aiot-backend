import { useState, useEffect } from "react";

export default function AlertBanner({ current, gasThreshold = 300 }) {
  const [visible, setVisible] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!current) return;
    const msgs = [];
    if (current.gas_ppm > gasThreshold)
      msgs.push(`Gas alert: ${current.gas_ppm.toFixed(0)} ppm`);
    if (current.door_open)
      msgs.push("Door is open");

    if (msgs.length > 0) {
      setMessage(msgs.join(" · "));
      setVisible(true);
      const timer = setTimeout(() => setVisible(false), 10000);
      return () => clearTimeout(timer);
    }
  }, [current, gasThreshold]);

  if (!visible) return null;

  return (
    <div className="alert-banner">
      <span>⚠ {message}</span>
      <button onClick={() => setVisible(false)}>✕</button>
    </div>
  );
}
