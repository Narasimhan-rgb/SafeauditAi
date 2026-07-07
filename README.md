# SafeAudit AI

> Privacy-aware edge-AI safety compliance monitoring for small manufacturing units.

SafeAudit AI is a solo prototype designed for MSME workshops that already use CCTV cameras. It turns local video into actionable PPE-compliance events, restricted-zone alerts, and simple safety reports without relying on continuous cloud video storage.

## Phase 1 MVP

The initial prototype will validate:

- Helmet and safety-vest compliance from a local video feed
- One configurable restricted or high-risk zone
- Timestamped violation logs with event screenshots
- Local event database and simple dashboard
- Privacy-aware event-only storage

## Why this matters

Small factories often record CCTV footage but review it only after an incident. SafeAudit AI aims to make existing cameras more useful by helping supervisors identify safety risks earlier, at lower cost.

## Technical direction

```text
Existing CCTV / test video
        ↓
Custom PPE object-detection model
        ↓
Zone and rule engine
        ↓
Violation event log
        ↓
Dashboard, report and alerts
```

Planned stack: Python, OpenCV, a custom PPE model, FastAPI, SQLite/PostgreSQL, React, and local edge deployment.

## Run modes

### Dashboard demo mode

Set this in `backend/.env` to test the dashboard, reviews, metrics, and CSV export without any model or video:

```text
DEMO_MODE=true
```

### Real PPE video mode

A custom local YOLO model is required. The model must recognise canonical classes:

```text
person
helmet
vest
```

Common names such as `Worker`, `Hardhat`, and `Safety Vest` are normalised automatically. Before setting `MODEL_PATH`, validate the model from the `backend` folder:

```cmd
pip install -r requirements-vision.txt
python -m app.scripts.check_ppe_model "D:\\path\\to\\ppe-model.pt"
```

Read `backend/models/README.md` before adding any model. Do not commit model weights.

## Honest scope

This is a prototype. It will not claim validated near-miss prediction, multi-camera tracking, industrial-grade face anonymisation, or safety certification until those capabilities are tested in a real pilot.

## Build roadmap

| Weeks | Output |
|---|---|
| 1–2 | Environment, test video pipeline, PPE dataset selection |
| 3–4 | First custom PPE model and local video demo |
| 5–6 | Zone configuration and event logging |
| 7–8 | Dashboard and alert integration |
| 9–12 | Edge-device benchmark, privacy improvements, tests |
| 13–16 | Pilot feedback, metrics, MSME prototype report |

## Repository rules

Never commit raw CCTV recordings, personal data, incident images from real workplaces, model weights without permission, `.env` files, or API keys.
