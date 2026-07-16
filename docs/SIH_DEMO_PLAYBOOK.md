# SafeAudit AI — SIH Demo Playbook

Use this playbook only when the selected SIH problem statement is a direct match for worker safety, PPE compliance, MSMEs or privacy-aware edge monitoring.

## Three-minute narrative

### 0:00–0:25 — Problem

Small workshops may already have CCTV, but supervisors cannot continuously watch every feed. Reviewing footage only after an incident provides evidence, not early operational awareness.

### 0:25–0:50 — Product decision

SafeAudit AI is a local decision-support layer. It checks helmet and vest presence only inside configured risk zones, retains event evidence rather than the full raw upload, and keeps the supervisor responsible for the final verdict.

### 0:50–1:25 — Readiness and zone

Show the readiness checklist. Explain that the product refuses real analysis until an authorised compatible model, optional vision packages and one zone are present. Configure the assembly bay and show the required PPE tags.

### 1:25–2:05 — Event flow

Use clearly labelled demo records for the stable walkthrough. If a verified model and authorised clip are available, run the real-video path separately. Open the supervisor queue and classify one event.

### 2:05–2:30 — Evidence boundary

Show the evaluation panel. Point out that demo events are excluded from real-video metrics and that review-based precision does not measure missed violations.

### 2:30–3:00 — Impact and next proof

Export the CSV report. End with the next measurable step: one controlled MSME pilot that records false alerts, missed violations, inference latency, lighting conditions and supervisor usability.

## Winning demo scenario

```text
Authorised clip
    ↓
Worker enters configured assembly zone
    ↓
Helmet or vest is not associated with the worker
    ↓
Reviewable event and evidence image are created
    ↓
Supervisor confirms, rejects or marks the event unclear
    ↓
Feedback appears in evaluation and CSV reporting
```

## Evidence checklist

| Judge concern | Evidence to show |
|---|---|
| Does it run? | Local dashboard, health endpoint and production frontend build |
| Is the AI real? | Compatible custom model checker output and authorised test run |
| Is it accurate? | Ground-truth table, per-condition results and false-alert examples |
| Is it privacy-aware? | Local architecture, upload cleanup and repository data rules |
| Is it practical? | Existing-camera direction, simple zone setup and deployment cost sheet |
| Is it responsible? | Human verdict, demo exclusion and explicit non-certification scope |
| Can it scale? | PostgreSQL-ready configuration and planned edge benchmark |

## Demo resilience

Carry all of the following to an internal or grand-finale demonstration:

- A clean local clone with dependencies installed.
- One-command Windows launcher.
- Seeded demo data for a deterministic walkthrough.
- A short authorised test clip and verified local model, when available.
- A recorded backup of the real-video run.
- Printed architecture, metric definitions and limitations.
- A downloaded CSV report.

Never depend on venue internet for the core demonstration.

## Questions and concise answers

| Question | Answer |
|---|---|
| Why not normal CCTV? | CCTV records footage; SafeAudit creates searchable, reviewable PPE events inside defined risk zones. |
| Is it real-time? | Phase 1 analyses short local videos. Real-time edge throughput is a planned benchmark, not a current claim. |
| Does it replace a safety officer? | No. The supervisor makes the final decision for every event. |
| What makes it privacy-aware? | Local processing direction, temporary raw-upload deletion and event-only evidence retention. Production still needs access and retention controls. |
| What is novel? | The product combines MSME retrofit constraints, local processing, explainable zone/PPE rules and a feedback boundary that separates demos from measured evidence. |
| What happens when AI is wrong? | The supervisor can mark false alarm or unclear; those outcomes are tracked for tuning and reporting. |
| What is the next deployment step? | One authorised single-camera pilot with ground truth, latency and usability measurement. |

## Claims that remain prohibited

- “Prevents accidents.”
- “99% accurate” without a reproducible evaluation.
- “Real-time” without target-device FPS and latency.
- “Certified” or “legally compliant.”
- “Near-miss prediction” before implementation and validation.
- “Anonymous” before anonymisation is technically tested.
