import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function useSensorData(pollInterval = 5000) {
  const [latest, setLatest] = useState([]);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  const fetchLatest = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/api/sensors/latest?limit=1`);
      setLatest(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/api/sensors/history?minutes=60`);
      setHistory(data);
    } catch {
      // silently fail on history
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      fetchLatest();
      fetchHistory();
    });
    const id = setInterval(() => {
      fetchLatest();
      fetchHistory();
    }, pollInterval);
    return () => clearInterval(id);
  }, [fetchLatest, fetchHistory, pollInterval]);

  const current = latest[0] || null;
  return { current, history, error };
}
