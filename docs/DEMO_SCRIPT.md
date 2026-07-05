# SafeAudit AI — Phase 1 Demo Script

Use this script for a 2–3 minute prototype demonstration. Only use authorised test footage.

## Before the demo

1. Start the FastAPI backend on port 8000.
2. Start the React dashboard.
3. Confirm the custom PPE model path is configured in `backend/.env`.
4. Use a short test clip containing a person, helmet and vest examples.
5. Do not use real workplace footage without written permission.

## Demo flow

### 1. Explain the problem — 20 seconds

Small MSME workshops may already have CCTV cameras, but supervisors often review footage only after an incident. Continuous manual PPE checking is difficult and costly.

### 2. Explain the Phase 1 scope — 20 seconds

This prototype checks helmet and vest compliance inside one configured safety zone. It creates an event log and retains only evidence images for review. It is not presented as a certified safety system or as a near-miss prediction system.

### 3. Configure a zone — 30 seconds

Create a rectangular safety zone in the dashboard using video-frame pixel coordinates. The zone defines where helmet and vest are required.

### 4. Run video analysis — 45 seconds

Upload an authorised short video. Explain that the local backend reads frames, the custom PPE model detects `person`, `helmet`, and `vest`, and the rule engine checks PPE only for workers inside the zone.

### 5. Review events — 30 seconds

Show the event table, severity, timestamp, evidence image, and CSV export. State clearly that a supervisor reviews every event before acting.

### 6. Explain the next validation step — 20 seconds

The next step is to measure false alerts, missed detections, latency, and usability with a controlled pilot. Future work includes edge-device benchmarking and stronger privacy controls.

## Questions evaluators may ask

| Question | Honest answer |
|---|---|
| Why not use normal CCTV? | Normal CCTV records video. SafeAudit AI turns authorised footage into searchable PPE events and reviewable reports. |
| Is it real-time? | The current MVP analyses short local videos. Real-time edge inference is a planned validation phase. |
| What makes it MSME-friendly? | It is designed as a low-cost retrofit around existing camera infrastructure and local processing. |
| Does it replace safety officers? | No. It supports supervisors; every event requires human review. |
| How will you protect privacy? | The MVP keeps event-only evidence and deletes raw uploads after processing. Production deployment needs policy controls, access roles, retention settings, and stronger anonymisation validation. |
