export default function LogTable({ logs, emptyMessage = "No activity yet." }) {
  return (
    <section className="log-panel" aria-label="Database log view">
      <div className="table-scroll">
        <table className="log-table">
          <thead>
            <tr>
              <th>Log_ID</th>
              <th>Timestamp</th>
              <th>Event_Type</th>
              <th>Source</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {logs.length ? (
              logs.map((log) => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>{log.timestamp}</td>
                  <td>
                    <span className={`log-type log-type--${log.type}`}>{log.type}</span>
                  </td>
                  <td>{log.source}</td>
                  <td>{log.message}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="empty-table">{emptyMessage}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="table-footer">
        <span>Showing {logs.length} local entries</span>
        <div>
          <button type="button" disabled>Prev</button>
          <button type="button">1</button>
          <button type="button" disabled>Next</button>
        </div>
      </div>
    </section>
  );
}
