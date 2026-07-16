# SafeAudit AI

> Privacy-aware, human-reviewed PPE and safety-zone monitoring for MSME pilots.

[![Full-stack checks](https://github.com/Narasimhan-rgb/SafeauditAiPrototype-/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/Narasimhan-rgb/SafeauditAiPrototype-/actions/workflows/backend-tests.yml)

SafeAudit AI is a Phase 1 product prototype being prepared by **Team RakshaEdge** for SIH 2026 problem-statement matching and controlled MSME validation. It turns an authorised local video into explainable PPE events, supervisor decisions and exportable safety records without retaining the complete raw upload.

This repository is honest about its maturity: the dashboard and review workflow are demonstrable; real detection requires an authorised custom PPE model and measured pilot evidence.

## Product promise

Small workshops may already record CCTV but still depend on continuous manual checking or post-incident review. SafeAudit AI adds a narrow decision-support layer:

```text
Authorised camera or short video
              ↓
      Local PPE detection
              ↓
   Configured safety-zone rules
              ↓
 Reviewable event-only evidence
              ↓
 Supervisor decision and CSV report
```

### Why the approach is different

- **Local-first processing:** the current workflow does not require continuous cloud-video storage.
- **Human accountability:** every generated event can be confirmed, rejected as a false alarm or marked unclear.
- **Evidence-aware reporting:** seeded demo data is excluded from real-video evaluation metrics.
- **Retrofit direction:** the product is designed around existing authorised cameras and short pilot clips.
- **Narrow, testable scope:** Phase 1 supports `person`, `helmet`, `vest` and rectangular zones only.

## Current status

| Capability | Status |
|---|---|
| SIH-ready operator dashboard | Complete |
| Local demo mode with labelled sample data | Complete |
| Safety-zone configuration and validation | Complete |
| Supervisor event-review workflow | Complete |
| CSV event report | Complete |
| Demo-excluding evaluation summary | Complete |
| Backend unit tests and frontend production build | Automated in CI |
| PPE model compatibility checker | Complete |
| Real PPE video analysis | Requires an authorised custom `.pt` model |
| MSME pilot evidence | Not yet collected |
| Near-miss prediction or certified safety automation | Outside the current scope |

## Judge-facing demo in three minutes

1. Show the local-first and human-review product promise.
2. Open the readiness checklist and explain every pilot prerequisite.
3. Configure one rectangular assembly-zone rule.
4. Walk through clearly marked demo events or run one authorised test clip.
5. Mark an event as confirmed, false alarm or unclear.
6. Show that demo data is excluded from validation figures.
7. Export the event report and state the next pilot measurement.

The complete demonstration and fallback plan is in [`docs/SIH_DEMO_PLAYBOOK.md`](docs/SIH_DEMO_PLAYBOOK.md).

## Windows quick start

Install Python 3.11+ and Node.js LTS once. Open Command Prompt in the repository folder and run:

```cmd
run-demo.cmd
```

The launcher:

1. Creates an isolated Python environment.
2. Installs backend and frontend packages.
3. Enables clearly labelled demo mode.
4. Seeds a local zone and two sample events.
5. Starts FastAPI and React in separate windows.
6. Opens `http://localhost:5173`.

Keep both service windows open during the walkthrough. Demo records are not camera or model results.

### Verify the project

Backend tests:

```cmd
run-tests.cmd
```

Frontend production build:

```cmd
cd frontend
npm install
npm run build
```

## Run modes

### Dashboard walkthrough

Use these values in `backend/.env`:

```text
MODEL_PATH=
DEMO_MODE=true
```

This mode verifies the dashboard, database, supervisor reviews, evaluation boundary and report export without claiming AI detection.

### Authorised PPE pilot

The model must recognise canonical classes:

```text
person
helmet
vest
```

Common compatible names such as `Worker`, `Hardhat` and `Safety Vest` are normalised. Validate an authorised local model:

```cmd
check-ppe-model.cmd "D:\models\ppe-model.pt"
```

When the checker reports `READY`, update `backend/.env`:

```text
MODEL_PATH=D:\models\ppe-model.pt
DEMO_MODE=false
```

Then run:

```cmd
start-pilot.cmd
```

Read [`backend/models/README.md`](backend/models/README.md) and [`docs/PILOT_START.md`](docs/PILOT_START.md) before using a model. Never commit weights or workplace footage.

## Technical structure

| Layer | Implementation |
|---|---|
| Dashboard | React 19 + Vite 7 |
| API | FastAPI |
| Local data | SQLite through SQLAlchemy; PostgreSQL-ready configuration |
| Vision adapter | Optional Ultralytics-compatible custom model |
| Rules | Explainable person–PPE association and rectangular zone checks |
| Evidence | Event images, metadata, reviews and CSV export |
| Verification | Python unit tests + React production build in GitHub Actions |

```text
frontend/                Operator dashboard
backend/app/main.py      API and cleanup workflow
backend/app/services/    Detection, rules, readiness and evaluation
backend/tests/           Deterministic unit tests
docs/                    Pilot, evaluation and SIH material
```

## Evidence required before stronger claims

Collect all of the following before quoting performance publicly:

1. Model checker output showing `READY`.
2. Written permission for the test video.
3. Manual ground truth for every test interval.
4. Review verdict for every generated real event.
5. False alarms, missed violations and unclear results.
6. Test device, resolution, lighting, camera angle and inference latency.
7. A completed [`docs/PILOT_VALIDATION_FORM.md`](docs/PILOT_VALIDATION_FORM.md).

Review-based precision alone does **not** measure missed violations. Follow [`docs/EVALUATION_PROTOCOL.md`](docs/EVALUATION_PROTOCOL.md) for any report or competition claim.

## Privacy and repository rules

Never commit:

- Raw CCTV recordings or personal data.
- Real workplace incident images.
- `.env` files, API keys or database files.
- Model weights without explicit redistribution permission.

The current synchronous video endpoint deletes the temporary raw upload in a `finally` cleanup step. Event evidence remains local for supervisor review. A production deployment still needs authentication, access control, configurable retention, audit logging and formally validated privacy controls.

## Honest scope

SafeAudit AI is decision support, not a replacement for safety personnel. It does not currently claim:

- Industrial or legal compliance certification.
- Guaranteed accident reduction.
- Validated near-miss prediction.
- Multi-camera or identity tracking.
- Production-grade face anonymisation.
- Fully autonomous disciplinary action.

## Roadmap

| Phase | Output |
|---|---|
| 1 — Demonstrate | Dashboard, zones, events, review, CSV, tests |
| 2 — Validate | Authorised custom model and controlled video evaluation |
| 3 — Pilot | One MSME deployment, latency measurement and false-alarm tuning |
| 4 — Harden | Edge benchmark, authentication, retention controls and alert integration |
| 5 — Commercialise | Repeatable installation, support model and paid site validation |
