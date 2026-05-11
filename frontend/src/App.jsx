import { useEffect, useMemo, useState } from "react";
import { useSensorData } from "./hooks/useSensorData";
import Dashboard from "./components/Dashboard";
import Controls from "./components/Controls";
import LogTable from "./components/LogTable";
import "./App.css";

const ROUTES = [
  { path: "/dashboard", label: "Dashboard", icon: "H" },
  { path: "/devices", label: "Devices", icon: "D" },
  { path: "/logs", label: "Logs", icon: "L" },
  { path: "/settings", label: "Settings", icon: "S" },
];

function normalizePath(pathname) {
  if (pathname === "/") return "/dashboard";
  return ROUTES.some((route) => route.path === pathname) ? pathname : "/dashboard";
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "Waiting for data";
  return new Date(timestamp).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function makeLogs(current, history, tempThreshold) {
  const sensorRows = history.slice(-6).reverse().map((row, index) => {
    const type = row.temperature > tempThreshold ? "warning" : "info";
    return {
      id: `LIVE-${String(history.length - index).padStart(4, "0")}`,
      timestamp: formatTimestamp(row.timestamp),
      type,
      source: row.temperature > tempThreshold ? "DHT11 Sensor" : "Sensor Stream",
      message:
        row.temperature > tempThreshold
          ? `Temperature exceeded threshold at ${Number(row.temperature).toFixed(1)}C.`
          : "Environment sample stored successfully.",
    };
  });

  if (sensorRows.length) return sensorRows;

  const now = current?.timestamp ? formatTimestamp(current.timestamp) : "No live timestamp";
  return [
    {
      id: "MOCK-1002",
      timestamp: now,
      type: current?.temperature > tempThreshold ? "warning" : "info",
      source: "DHT11 Sensor",
      message:
        current?.temperature != null
          ? `Room temperature is ${Number(current.temperature).toFixed(1)}C.`
          : "Temperature sensor is waiting for data.",
    },
    {
      id: "MOCK-1001",
      timestamp: now,
      type: "info",
      source: "Local Gateway",
      message: "Dashboard running in offline-friendly mode.",
    },
  ];
}

export default function App() {
  const { current, history, error } = useSensorData(5000);
  const [page, setPage] = useState(() => normalizePath(window.location.pathname));
  const [tempThreshold, setTempThreshold] = useState(26);

  useEffect(() => {
    const onPopState = () => setPage(normalizePath(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    const normalized = normalizePath(window.location.pathname);
    if (window.location.pathname !== normalized) {
      window.history.replaceState({}, "", normalized);
    }
  }, []);

  function navigate(path) {
    const nextPath = normalizePath(path);
    setPage(nextPath);
    window.history.pushState({}, "", nextPath);
  }

  function handleThreshold(type, value) {
    if (type === "temp") setTempThreshold(value);
  }

  const logs = useMemo(
    () => makeLogs(current, history, tempThreshold),
    [current, history, tempThreshold],
  );

  const activeTitle = ROUTES.find((route) => route.path === page)?.label || "Dashboard";
  const hasAlert = current?.temperature > tempThreshold;

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand-lockup">
          <span className="brand-mark">Y</span>
          <div>
            <strong>YOLO:HOME</strong>
            <span>Warm safety console</span>
          </div>
        </div>
        <nav className="nav-stack">
          {ROUTES.map((route) => (
            <button
              key={route.path}
              className={`nav-item ${page === route.path ? "nav-item--active" : ""}`}
              type="button"
              onClick={() => navigate(route.path)}
            >
              <span>{route.icon}</span>
              {route.label}
            </button>
          ))}
        </nav>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <span className="eyebrow">Smart home</span>
            <h1>{activeTitle}</h1>
          </div>
          <label className="search-box">
            <span>Search</span>
            <input type="search" placeholder="Search rooms, logs, or devices" />
          </label>
          <div className={`top-status ${hasAlert ? "top-status--alert" : ""}`}>
            <span>{hasAlert ? "Needs attention" : "Home steady"}</span>
            <strong>{formatTimestamp(current?.timestamp)}</strong>
          </div>
        </header>

        <main className="page-surface">
          {error && (
            <div className="connection-error">
              <strong>Backend offline</strong>
              <span>{error}</span>
            </div>
          )}

          {page === "/dashboard" && (
            <Dashboard
              current={current}
              history={history}
              logs={logs}
              tempThreshold={tempThreshold}
              onThresholdChange={handleThreshold}
            />
          )}
          {page === "/devices" && (
            <DevicesPage
              tempThreshold={tempThreshold}
              onThresholdChange={handleThreshold}
            />
          )}
          {page === "/logs" && <LogsPage logs={logs} />}
          {page === "/settings" && <SettingsPage />}
        </main>

        <nav className="mobile-nav" aria-label="Mobile navigation">
          {ROUTES.map((route) => (
            <button
              key={route.path}
              className={`mobile-nav__item ${page === route.path ? "mobile-nav__item--active" : ""}`}
              type="button"
              onClick={() => navigate(route.path)}
            >
              <span>{route.icon}</span>
              {route.label}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
}

function DevicesPage({ tempThreshold, onThresholdChange }) {
  const [rules, setRules] = useState({
    lighting: true,
    climate: true,
    away: false,
  });

  function toggleRule(key) {
    setRules((current) => ({ ...current, [key]: !current[key] }));
  }

  return (
    <div className="page-stack page-stack--narrow">
      <section className="warm-panel">
        <div className="section-heading">
          <span className="eyebrow">Automation preferences</span>
          <h2>Device behavior</h2>
        </div>
        <div className="toggle-grid">
          <ToggleCard
            title="Smart lighting"
            description="React to low ambient light."
            active={rules.lighting}
            onToggle={() => toggleRule("lighting")}
          />
          <ToggleCard
            title="Climate response"
            description="Use the fan when the room is too warm."
            active={rules.climate}
            onToggle={() => toggleRule("climate")}
          />
          <ToggleCard
            title="Away mode"
            description="Prefer stricter alerting while away."
            active={rules.away}
            onToggle={() => toggleRule("away")}
          />
        </div>
      </section>

      <Controls
        tempThreshold={tempThreshold}
        onThresholdChange={onThresholdChange}
      />
    </div>
  );
}

function LogsPage({ logs }) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");

  const filteredLogs = logs.filter((log) => {
    const haystack = `${log.id} ${log.source} ${log.message}`.toLowerCase();
    return (
      (filter === "all" || log.type === filter) &&
      haystack.includes(query.trim().toLowerCase())
    );
  });

  return (
    <div className="page-stack">
      <section className="warm-panel">
        <div className="logs-toolbar">
          <div className="section-heading">
            <span className="eyebrow">Database log view</span>
            <h2>Activity history</h2>
          </div>
          <label className="search-box search-box--panel">
            <span>Search</span>
            <input
              type="search"
              placeholder="Search ID, source, or message"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        </div>
        <div className="filter-row" aria-label="Log filters">
          {["all", "info", "warning", "critical"].map((type) => (
            <button
              key={type}
              className={filter === type ? "filter-chip filter-chip--active" : "filter-chip"}
              type="button"
              onClick={() => setFilter(type)}
            >
              {type}
            </button>
          ))}
        </div>
      </section>
      <LogTable logs={filteredLogs} emptyMessage="No logs matched your filters." />
    </div>
  );
}

function SettingsPage() {
  const [profile, setProfile] = useState({
    name: "Jane Doe",
    email: "jane.doe@example.com",
    phone: "+1 555 123 4567",
    emailAlerts: true,
    pushAlerts: true,
    smsAlerts: false,
  });

  function updateProfile(key, value) {
    setProfile((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
  }

  return (
    <div className="settings-layout">
      <section className="warm-panel owner-panel">
        <div className="avatar-mark">JD</div>
        <h2>{profile.name}</h2>
        <p>Primary Owner</p>
        <div className="owner-stats">
          <span>
            <strong>3</strong>
            Devices
          </span>
          <span>
            <strong>4</strong>
            Rules
          </span>
        </div>
      </section>

      <form className="warm-panel settings-form" onSubmit={handleSubmit}>
        <div className="section-heading">
          <span className="eyebrow">Settings</span>
          <h2>Profile and notifications</h2>
        </div>
        <label>
          <span>Name</span>
          <input value={profile.name} onChange={(event) => updateProfile("name", event.target.value)} />
        </label>
        <label>
          <span>Email</span>
          <input
            type="email"
            value={profile.email}
            onChange={(event) => updateProfile("email", event.target.value)}
          />
        </label>
        <label>
          <span>Phone</span>
          <input value={profile.phone} onChange={(event) => updateProfile("phone", event.target.value)} />
        </label>

        <div className="notification-list">
          <ToggleCard
            title="Email alerts"
            description="Daily summaries and critical alerts."
            active={profile.emailAlerts}
            onToggle={() => updateProfile("emailAlerts", !profile.emailAlerts)}
          />
          <ToggleCard
            title="Push notifications"
            description="Immediate state changes on mobile."
            active={profile.pushAlerts}
            onToggle={() => updateProfile("pushAlerts", !profile.pushAlerts)}
          />
          <ToggleCard
            title="SMS alerts"
            description="Severe alerts only."
            active={profile.smsAlerts}
            onToggle={() => updateProfile("smsAlerts", !profile.smsAlerts)}
          />
        </div>

        <button className="save-btn" type="submit">Save changes</button>
      </form>
    </div>
  );
}

function ToggleCard({ title, description, active, onToggle }) {
  return (
    <div className={`toggle-card ${active ? "toggle-card--active" : ""}`}>
      <div>
        <strong>{title}</strong>
        <span>{description}</span>
      </div>
      <button
        className={`switch ${active ? "switch--on" : ""}`}
        type="button"
        aria-pressed={active}
        aria-label={title}
        onClick={onToggle}
      >
        <span />
      </button>
    </div>
  );
}
