import { useState, useEffect, useMemo } from "react";

export default function AlertBanner({ current, tempThreshold = 26 }) {
  const [dismissedMessage, setDismissedMessage] = useState("");
  const message = useMemo(() => {
    if (!current) return;
    const msgs = [];
    if (current.temperature > tempThreshold)
      msgs.push(`Temperature alert: ${current.temperature.toFixed(1)}C`);

    return msgs.join(" · ");
  }, [current, tempThreshold]);

  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(() => setDismissedMessage(message), 10000);
    return () => clearTimeout(timer);
  }, [message]);

  if (!message || dismissedMessage === message) return null;

  return (
    <div className="alert-banner" role="status">
      <div>
        <span>Attention needed</span>
        <strong>{message}</strong>
      </div>
      <button type="button" aria-label="Dismiss alert" onClick={() => setDismissedMessage(message)}>
        Close
      </button>
    </div>
  );
}
