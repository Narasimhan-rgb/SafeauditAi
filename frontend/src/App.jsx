import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";
const FILE_BASE = API_BASE.replace("/api/v1", "");
const DEMO_SOURCE = "safeaudit-local-demo";

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

function displayLabel(value) {
  return value.replaceAll("_", " ");
}

function displayPercent(value) {
  return value === null || value === undefined ? "Not available" : `${(value * 100).toFixed(1)}%`;
}

async function responseJson(response, fallbackMessage) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || fallbackMessage);
  }
  return payload;
}

function MetricCard({ label, value, tone = "neutral", detail }) {
  return (
    <article className={`metric-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function CheckItem({ label, complete }) {
  return (
    <li className={complete ? "complete" : "pending"}>
      <span aria-hidden="true">{complete ? "✓" : "·"}</span>
      {label}
    </li>
  );
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
  const [eventQuery, setEventQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [zoneForm, setZoneForm] = useState({ name: "Assembly Bay", coordinates: "80,80,500,430" });

  const reviewByEventId = useMemo(
    () => Object.fromEntries(reviews.map((review) => [review.event_id, review])),
    [reviews],
  );

  const visibleEvents = useMemo(() => {
    const query = eventQuery.trim().toLowerCase();
    return events.filter((event) => {
      const matchesSeverity = severityFilter === "all" || event.severity === severityFilter;
      const matchesQuery = !query || [event.message, event.event_type, event.source_name]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(query));
      return matchesSeverity && matchesQuery;
    });
  }, [eventQuery, events, severityFilter]);

  const pendingReviews = Math.max(metrics.total_events - metrics.reviewed_events, 0);
  const systemMode = readiness.demo_mode ? "Demo walkthrough" : "Pilot preparation";

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");
      const endpoints = ["events", "zones", "metrics", "readiness", "reviews", "evaluation/summary"];
      const responses = await Promise.all(endpoints.map((endpoint) => fetch(`${API_BASE}/${endpoint}`)));
      const payloads = await Promise.all(
        responses.map((response, index) => responseJson(response, `Unable to load ${endpoints[index]}.`)),
      );
      const [eventsPayload, zonesPayload, metricsPayload, readinessPayload, reviewsPayload, evaluationPayload] = payloads;
      setEvents(eventsPayload);
      setZones(zonesPayload);
      setMetrics(metricsPayload);
      setReadiness(readinessPayload);
      setReviews(reviewsPayload);
      setEvaluation(evaluationPayload);
    } catch (err) {
      setError(`${err.message} Confirm that the local FastAPI service is running on port 8000.`);
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
      setError("Enter zone coordinates as x1,y1,x2,y2. Example: 80,80,500,430.");
      return;
    }
    if (coordinates.some((value) => value < 0) || coordinates[2] <= coordinates[0] || coordinates[3] <= coordinates[1]) {
      setError("Coordinates must be non-negative and follow x1 < x2 and y1 < y2.");
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
      await responseJson(response, "Unable to create safety zone.");
      setStatus("Safety zone saved. The rule engine will require a helmet and vest inside this area.");
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
      setError("Resolve every readiness blocker before analysing a video.");
      return;
    }

    try {
      setAnalysing(true);
      setError("");
      setStatus("Analysing locally. The temporary raw upload will be deleted when processing finishes.");
      const formData = new FormData();
      formData.append("file", selectedVideo);
      const response = await fetch(`${API_BASE}/analysis/video`, { method: "POST", body: formData });
      const payload = await responseJson(response, "Video analysis failed.");
      setStatus(`${payload.message} Sampled frames: ${payload.processed_frames}; reviewable events: ${payload.events_created}.`);
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
      const payload = await responseJson(response, "Unable to save review.");
      setStatus(`Event #${eventId} marked as ${displayVerdict(payload.verdict)}.`);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingReviewId(null);
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#workspace">Skip to workspace</a>
      <header className="topbar">
        <a className="brand" href="#top" aria-label="SafeAudit AI home">
          <span className="brand-mark" aria-hidden="true">S</span>
          <span><strong>SafeAudit AI</strong><small>by Team RakshaEdge</small></span>
        </a>
        <nav aria-label="Dashboard sections">
          <a href="#readiness">Readiness</a>
          <a href="#workspace">Workspace</a>
          <a href="#events">Events</a>
        </nav>
        <div className="system-chip">
          <span className={loading || error ? "status-dot warning" : "status-dot"} aria-hidden="true" />
          {loading ? "Connecting" : error ? "Service check" : systemMode}
        </div>
      </header>

      <main className="page" id="top">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">SIH 2026 PRODUCT BUILD · PRIVACY-AWARE EDGE AI</p>
            <h1 id="hero-title">Turn existing CCTV into reviewable safety signals.</h1>
            <p className="hero-text">
              SafeAudit AI helps small workshops detect PPE gaps inside configured risk zones, retain only event evidence,
              and keep a human supervisor responsible for the final decision.
            </p>
            <div className="hero-actions">
              <a className="primary-button" href="#workspace">Open operator workspace</a>
              <a className="secondary-button" href={`${API_BASE}/reports/events.csv`}>Export event report</a>
            </div>
            <div className="trust-row" aria-label="Product principles">
              <span>Local processing</span><span>Event-only evidence</span><span>Human-reviewed alerts</span>
            </div>
          </div>
          <aside className="promise-card" aria-label="Local-first product promise">
            <p className="eyebrow">LOCAL-FIRST PROMISE</p>
            <h2>Designed for practical MSME pilots</h2>
            <ul>
              <li><span>01</span>Reuse an authorised camera or short test clip.</li>
              <li><span>02</span>Delete the temporary raw upload after analysis.</li>
              <li><span>03</span>Ask a supervisor to verify every generated event.</li>
            </ul>
            <p className="scope-tag">Phase 1 · PPE + rectangular safety zones</p>
          </aside>
        </section>

        <section className="metrics-grid" aria-label="Safety operations summary">
          <MetricCard label="Total events" value={metrics.total_events} detail={`${metrics.events_last_24h} in the last 24 hours`} />
          <MetricCard label="High priority" value={metrics.high_risk_events} tone="danger" detail="Helmet or multiple PPE gaps" />
          <MetricCard label="Awaiting review" value={pendingReviews} tone="warning" detail="Human decision still required" />
          <MetricCard label="Confirmed" value={metrics.confirmed_violations} tone="success" detail="Supervisor-verified violations" />
          <MetricCard label="False alarms" value={metrics.false_alarms} detail="Feedback for model tuning" />
          <MetricCard label="Active zones" value={metrics.configured_zones} detail="Configured monitoring areas" />
        </section>

        <section className="workflow-strip" aria-label="SafeAudit workflow">
          <div><span>1</span><strong>Observe</strong><small>Read an authorised local video</small></div>
          <div><span>2</span><strong>Explain</strong><small>Apply simple PPE and zone rules</small></div>
          <div><span>3</span><strong>Review</strong><small>Let a supervisor confirm the event</small></div>
          <div><span>4</span><strong>Improve</strong><small>Use feedback to reduce false alerts</small></div>
        </section>

        <section id="readiness" className={`readiness-panel ${readiness.ready_for_test ? "ready" : "blocked"}`} aria-labelledby="readiness-title">
          <div className="readiness-copy">
            <p className="eyebrow">PILOT READINESS</p>
            <h2 id="readiness-title">{readiness.ready_for_test ? "Ready for an authorised local test" : "Complete the setup before video analysis"}</h2>
            <p>{readiness.scope_note}</p>
            {readiness.demo_mode && <p className="demo-note"><strong>Demo mode:</strong> {readiness.demo_note}</p>}
          </div>
          <ul className="checklist">
            <CheckItem label="Custom model configured" complete={readiness.model_configured} />
            <CheckItem label="Model file found locally" complete={readiness.model_file_found} />
            <CheckItem label="Vision dependencies installed" complete={readiness.vision_dependencies_ready} />
            <CheckItem label="At least one zone configured" complete={readiness.configured_zones > 0} />
          </ul>
          {!readiness.ready_for_test && (
            <div className="blocker-list">
              {readiness.blockers.map((blocker) => <p key={blocker}>{blocker}</p>)}
            </div>
          )}
        </section>

        <section id="workspace" className="section-heading">
          <div><p className="eyebrow">OPERATOR WORKSPACE</p><h2>Configure, analyse and review</h2></div>
          <p>Keep the first test narrow: one camera, one rectangular zone and an authorised clip under 100 MB.</p>
        </section>

        <section className="workspace-grid">
          <form className="panel form-panel" onSubmit={createZone}>
            <div className="panel-title"><span>01</span><div><h3>Configure a safety zone</h3><p>Define where a helmet and vest are required.</p></div></div>
            <label>Zone name<input value={zoneForm.name} onChange={(event) => setZoneForm({ ...zoneForm, name: event.target.value })} required /></label>
            <label>Rectangle coordinates<input value={zoneForm.coordinates} onChange={(event) => setZoneForm({ ...zoneForm, coordinates: event.target.value })} required aria-describedby="coordinate-help" /></label>
            <p className="field-help" id="coordinate-help">Frame pixels: x1,y1,x2,y2 · Example 80,80,500,430</p>
            <div className="ppe-tags"><span>Helmet required</span><span>Vest required</span></div>
            <button type="submit">Save safety zone</button>
            <div className="zone-list">
              <strong>Configured zones</strong>
              {zones.length === 0 ? <p>No zone configured yet.</p> : zones.map((zone) => (
                <p key={zone.id}><span>{zone.name}</span><small>{zone.coordinates.join(", ")} · {zone.required_ppe.join(" + ")}</small></p>
              ))}
            </div>
          </form>

          <form className="panel form-panel" onSubmit={analyseVideo}>
            <div className="panel-title"><span>02</span><div><h3>Analyse an authorised clip</h3><p>Run inference locally and retain only event evidence.</p></div></div>
            <label className="file-drop">
              <span>{selectedVideo ? selectedVideo.name : "Choose MP4, AVI, MOV or MKV"}</span>
              <small>{selectedVideo ? `${(selectedVideo.size / 1024 / 1024).toFixed(1)} MB selected` : "Maximum 100 MB for this prototype"}</small>
              <input type="file" accept="video/mp4,video/avi,video/quicktime,video/x-matroska" onChange={(event) => setSelectedVideo(event.target.files?.[0] || null)} />
            </label>
            <button type="submit" disabled={analysing || !readiness.ready_for_test}>{analysing ? "Analysing locally…" : "Run local analysis"}</button>
            <div className="privacy-note"><strong>Privacy control</strong><p>The backend removes the temporary raw upload in a guaranteed cleanup step after success or failure.</p></div>
          </form>
        </section>

        <div className="message-stack" aria-live="polite">
          {status && <p className="notice">{status}</p>}
          {error && <p className="error" role="alert">{error}</p>}
        </div>

        <section className="panel evaluation-panel" aria-labelledby="evaluation-title">
          <div className="panel-heading">
            <div><p className="eyebrow">EVIDENCE, NOT CLAIMS</p><h2 id="evaluation-title">Prototype evaluation</h2></div>
            <span className={evaluation.ready_for_reporting ? "reporting-badge ready" : "reporting-badge"}>
              {evaluation.ready_for_reporting ? "Review evidence available" : "Validation pending"}
            </span>
          </div>
          <p>Seeded demo records remain visible for walkthroughs but are excluded from the validation figures below.</p>
          <div className="evaluation-grid">
            <article><span>Real events</span><strong>{evaluation.real_events}</strong></article>
            <article><span>Reviewed real events</span><strong>{evaluation.reviewed_real_events}</strong></article>
            <article><span>Review coverage</span><strong>{displayPercent(evaluation.review_rate)}</strong></article>
            <article><span>Review-based precision</span><strong>{displayPercent(evaluation.precision)}</strong></article>
          </div>
          <p className="method-note">{evaluation.note}</p>
        </section>

        <section id="events" className="panel events-panel" aria-labelledby="events-title">
          <div className="panel-heading event-heading">
            <div><p className="eyebrow">SUPERVISOR QUEUE</p><h2 id="events-title">Reviewable safety events</h2></div>
            <div className="event-filters">
              <label><span className="sr-only">Search events</span><input type="search" placeholder="Search event or source" value={eventQuery} onChange={(event) => setEventQuery(event.target.value)} /></label>
              <label><span className="sr-only">Filter severity</span><select value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}><option value="all">All severities</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label>
              <button className="secondary-button" type="button" onClick={loadDashboard}>Refresh</button>
            </div>
          </div>

          {loading && <p className="empty-state">Connecting to the local event store…</p>}
          {!loading && !error && events.length === 0 && <p className="empty-state">No events yet. Use demo mode for a walkthrough or configure a model for an authorised video test.</p>}
          {!loading && events.length > 0 && visibleEvents.length === 0 && <p className="empty-state">No events match the current filters.</p>}
          {!loading && visibleEvents.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Recorded</th><th>Signal</th><th>Priority</th><th>Explanation</th><th>Evidence</th><th>Supervisor decision</th></tr></thead>
                <tbody>
                  {visibleEvents.map((event) => {
                    const review = reviewByEventId[event.id];
                    const isDemo = event.source_name === DEMO_SOURCE;
                    return (
                      <tr key={event.id}>
                        <td><strong>{new Date(event.created_at).toLocaleDateString()}</strong><small>{new Date(event.created_at).toLocaleTimeString()}</small></td>
                        <td><span className="event-type">{displayLabel(event.event_type)}</span>{isDemo && <span className="demo-label">Demo</span>}</td>
                        <td><span className={`badge ${event.severity}`}>{event.severity}</span></td>
                        <td>{event.message}</td>
                        <td>{event.evidence_path ? <a href={`${FILE_BASE}${event.evidence_path}`} target="_blank" rel="noreferrer">Open image</a> : <span className="muted">No image</span>}</td>
                        <td>
                          <select className="review-select" aria-label={`Review event ${event.id}`} value={review?.verdict || ""} disabled={savingReviewId === event.id} onChange={(changeEvent) => saveReview(event.id, changeEvent.target.value)}>
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

      <footer>
        <div><strong>SafeAudit AI</strong><span>Privacy-aware safety decision support for MSME pilots.</span></div>
        <p>Prototype only · No face recognition · No safety certification claim · Human review required</p>
      </footer>
    </div>
  );
}
