import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export default function App() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadEvents() {
    try {
      setLoading(true);
      setError("");
      const response = await fetch(`${API_BASE}/events`);
      if (!response.ok) throw new Error("Unable to load safety events.");
      setEvents(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadEvents();
  }, []);

  const highRiskCount = events.filter((event) => event.severity === "high").length;

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">PHASE 1 MVP</p>
          <h1>SafeAudit AI</h1>
          <p className="subtitle">Local PPE and restricted-zone safety event dashboard.</p>
        </div>
        <button onClick={loadEvents}>Refresh events</button>
      </header>

      <section className="cards" aria-label="Safety summary">
        <article><span>Total events</span><strong>{events.length}</strong></article>
        <article><span>High-risk events</span><strong>{highRiskCount}</strong></article>
        <article><span>Storage policy</span><strong>Event-only</strong></article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Recent safety events</h2>
            <p>Model-generated events will appear here after PPE inference is connected.</p>
          </div>
        </div>

        {loading && <p>Loading events…</p>}
        {error && <p className="error">{error} Start the FastAPI backend on port 8000.</p>}
        {!loading && !error && events.length === 0 && (
          <p>No events yet. Use the API docs to create a test event before model integration.</p>
        )}
        {!loading && !error && events.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Time</th><th>Type</th><th>Severity</th><th>Message</th><th>Source</th></tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr key={event.id}>
                    <td>{new Date(event.created_at).toLocaleString()}</td>
                    <td>{event.event_type}</td>
                    <td><span className={`badge ${event.severity}`}>{event.severity}</span></td>
                    <td>{event.message}</td>
                    <td>{event.source_name || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
