import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";
const FILE_BASE = API_BASE.replace("/api/v1", "");

const INITIAL_READINESS = {
  ready_for_test: false,
  model_configured: false,
  model_file_found: false,
  vision_dependencies_ready: false,
  configured_zones: 0,
  demo_mode: false,
  blockers: ["Loading local MVP readiness…"],
  scope_note: "",
  demo_note: "",
};

const INITIAL_EVALUATION = {
  real_events: 0,
  demo_events: 0,
  reviewed_real_events: 0,
  confirmed_violations: 0,
  false_alarms: 0,
  unclear_events: 0,
  precision: null,
  review_rate: 0,
  ready_for_reporting: false,
  note: "Loading evaluation summary…",
};

function displayVerdict(verdict) {
  return verdict.replaceAll("_", " ");
}

function displayPercent(value) {
  return value === null || value === undefined ? "Not available" : `${(value * 100).toFixed(1)}%`;
}

export default function App() {
  const [events, setEvents] = useState([]);
  const [zones, setZones] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [metrics, setMetrics] = useState({
    total_events: 0,
    high_risk_events: 0,
    events_last_24h: 0,
    configured_zones: 0,
    reviewed_events: 0,
    confirmed_violations: 0,
    false_alarms: 0,
  });
  const [readiness, setReadiness] = useState(INITIAL_READINESS);
  const [evaluation, setEvaluation] = useState(INITIAL_EVALUATION);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [analysing, setAnalysing] = useState(false);
  const [savingReviewId, setSavingReviewId] = useState(null);
  const [zoneForm, setZoneForm] = useState({ name: "Assembly Bay", coordinates: "80,80,500,430" });

  const reviewByEventId = useMemo(
    () => Object.fromEntries(reviews.map((review) => [review.event_id, review])),
    [reviews],
  );

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");
      const [eventsResponse, zonesResponse, metricsResponse, readinessResponse, reviewsResponse, evaluationResponse] = await Promise.all([
        fetch(`${API_BASE}/events`),
        fetch(`${API_BASE}/zones`),
        fetch(`${API_BASE}/metrics`),
        fetch(`${API_BASE}/readiness`),
        fetch(`${API_BASE}/reviews`),
        fetch(`${API_BASE}/evaluation/summary`),
      ]);
      if (!eventsResponse.ok || !zonesResponse.ok || !metricsResponse.ok || !readinessResponse.ok || !reviewsResponse.ok || !evaluationResponse.ok) {
        throw new Error("Unable to load SafeAudit data.");
      }
      setEvents(await eventsResponse.json());
      setZones(await zonesResponse.json());
      setMetrics(await metricsResponse.json());
      setReadiness(await readinessResponse.json());
      setReviews(await reviewsResponse.json());
      setEvaluation(await evaluationResponse.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  async function createZone(event) {
    event.preventDefault();
    const coordinates = zoneForm.coordinates.split(",").map((value) => Number(value.trim()));
    if (coordinates.length !== 4 || coordinates.some(Number.isNaN)) {
      setError("Enter zone coordinates as x1,y1,x2,y2. Example: 80,80,500,430");
      return;
    }

    try {
      setStatus("");
      setError("");
      const response = await fetch(`${API_BASE}/zones`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: zoneForm.name, required_ppe: ["helmet", "vest"], coordinates }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Unable to create safety zone.");
      setStatus("Safety zone saved. You can now analyse a short authorised test clip.");
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    }
  }

  async function analyseVideo(event) {
    event.preventDefault();
    if (!selectedVideo) {
      setError("Choose a short authorised test video first.");
      return;
    }
    if (!readiness.ready_for_test) {
      setError("Complete the setup checks in MVP test readiness before analysing a video.");
      return;
    }

    try {
      setAnalysing(true);
      setError("");
      setStatus("Analysing video locally. Keep this browser tab open.");
      const formData = new FormData();
      formData.append("file", selectedVideo);
      const response = await fetch(`${API_BASE}/analysis/video`, { method: "POST", body: formData });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Video analysis failed.");
      setStatus(`${payload.message} Frames processed: ${payload.processed_frames}; events created: ${payload.events_created}.`);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setAnalysing(false);
    }
  }

  async function saveReview(eventId, verdict) {
    if (!verdict) return;
    try {
      setSavingReviewId(eventId);
      setError("");
      const response = await fetch(`${API_BASE}/events/${eventId}/review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ verdict, reviewer_note: "" }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Unable to save review.");
      setStatus(`Event #${eventId} marked as ${displayVerdict(payload.verdict)}.`);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingReviewId(null);
    }
  }

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">PHASE 1 MVP</p>
          <h1>SafeAudit AI</h1>
          <p className="subtitle">Local PPE and restricted-zone safety event dashboard.</p>
        </div>
        <div className="header-actions">
          {readiness.demo_mode && <span className="demo-pill">DEMO MODE</span>}
          <a className="secondary-button" href={`${API_BASE}/reports/events.csv`}>Download event CSV</a>
          <button onClick={loadDashboard}>Refresh</button>
        </div>
      </header>

      <section className={`readiness ${readiness.ready_for_test ? "ready" : "blocked"}`} aria-label="MVP test readiness">
        <div>
          <p className="eyebrow">MVP TEST READINESS</p>
          <h2>{readiness.ready_for_test ? "Ready for an authorised local test" : "Setup required before video analysis"}</h2>
          <p>{readiness.scope_note}</p>
          {readiness.demo_mode && <p><strong>Dashboard walkthrough is available:</strong> {readiness.demo_note}</p>}
        </div>
        {!readiness.ready_for_test && (
          <ul>
            {readiness.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}
          </ul>
        )}
      </section>

      <section className="cards" aria-label="Safety summary">
        <article><span>Total events</span><strong>{metrics.total_events}</strong></article>
        <article><span>High-risk events</span><strong>{metrics.high_risk_events}</strong></article>
        <article><span>Reviewed events</span><strong>{metrics.reviewed_events}</strong></article>
        <article><span>Confirmed violations</span><strong>{metrics.confirmed_violations}</strong></article>
        <article><span>False alarms</span><strong>{metrics.false_alarms}</strong></article>
        <article><span>Events in 24 hours</span><strong>{metrics.events_last_24h}</strong></article>
        <article><span>Configured zones</span><strong>{metrics.configured_zones}</strong></article>
      </section>

      <section className="workspace">
        <form className="panel form-panel" onSubmit={createZone}>
          <h2>1. Configure a safety zone</h2>
          <p>Use frame pixels from your test video. Start with one simple rectangular zone.</p>
          <label>Zone name<input value={zoneForm.name} onChange={(event) => setZoneForm({ ...zoneForm, name: event.target.value })} required /></label>
          <label>Coordinates<input value={zoneForm.coordinates} onChange={(event) => setZoneForm({ ...zoneForm, coordinates: event.target.value })} required /></label>
          <button type="submit">Save safety zone</button>
          <div className="zone-list">
            {zones.length === 0 ? <p>No zone configured yet.</p> : zones.map((zone) => <p key={zone.id}><strong>{zone.name}</strong> · {zone.required_ppe.join(", ")}</p>)}
          </div>
        </form>

        <form className="panel form-panel" onSubmit={analyseVideo}>
          <h2>2. Analyse a short test video</h2>
          <p>Use only authorised footage. The raw upload is deleted after analysis; violation evidence images are retained locally.</p>
          <label>Video file<input type="file" accept="video/mp4,video/avi,video/quicktime,video/x-matroska" onChange={(event) => setSelectedVideo(event.target.files?.[0] || null)} /></label>
          <button type="submit" disabled={analysing || !readiness.ready_for_test}>{analysing ? "Analysing…" : "Run local analysis"}</button>
          <p className="hint">Requires an authorised custom model with <code>person</code>, <code>helmet</code>, and <code>vest</code> labels.</p>
        </form>
      </section>

      {status && <p className="notice">{status}</p>}
      {error && <p className="error">{error} Start the FastAPI backend on port 8000 and check its API docs.</p>}

      <section className="panel evaluation-panel">
        <div className="panel-heading">
          <h2>Prototype evaluation</h2>
          <p>Only real local-video events are counted below. Seeded demo records are excluded from validation metrics.</p>
        </div>
        <div className="evaluation-grid">
          <article><span>Real events</span><strong>{evaluation.real_events}</strong></article>
          <article><span>Reviewed real events</span><strong>{evaluation.reviewed_real_events}</strong></article>
          <article><span>Review rate</span><strong>{displayPercent(evaluation.review_rate)}</strong></article>
          <article><span>Review-based precision</span><strong>{displayPercent(evaluation.precision)}</strong></article>
        </div>
        <p className={evaluation.ready_for_reporting ? "notice" : "hint"}>
          {evaluation.ready_for_reporting
            ? "Review-based precision is available. Add the manual ground-truth log before using it in a report."
            : "No reviewed real events yet. Demo clicks do not count as model validation."}
        </p>
        <p className="hint">{evaluation.note}</p>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Recent safety events</h2>
            <p>Review each model result. This feedback identifies false alarms and builds pilot evidence for the MVP.</p>
          </div>
        </div>

        {loading && <p>Loading dashboard…</p>}
        {!loading && !error && events.length === 0 && <p>No events yet. Save a zone, configure the model, then analyse a short test clip.</p>}
        {!loading && events.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Time</th><th>Type</th><th>Severity</th><th>Message</th><th>Evidence</th><th>Supervisor review</th></tr></thead>
              <tbody>
                {events.map((event) => {
                  const review = reviewByEventId[event.id];
                  return (
                    <tr key={event.id}>
                      <td>{new Date(event.created_at).toLocaleString()}</td>
                      <td>{event.event_type}</td>
                      <td><span className={`badge ${event.severity}`}>{event.severity}</span></td>
                      <td>{event.message}</td>
                      <td>{event.evidence_path ? <a href={`${FILE_BASE}${event.evidence_path}`} target="_blank" rel="noreferrer">Review image</a> : "—"}</td>
                      <td>
                        <select
                          className="review-select"
                          value={review?.verdict || ""}
                          disabled={savingReviewId === event.id}
                          onChange={(changeEvent) => saveReview(event.id, changeEvent.target.value)}
                        >
                          <option value="">Mark result…</option>
                          <option value="confirmed_violation">Confirmed violation</option>
                          <option value="false_alarm">False alarm</option>
                          <option value="unclear">Unclear</option>
                        </select>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
