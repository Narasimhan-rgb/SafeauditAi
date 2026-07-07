# Authorised Local PPE Pilot Checklist

Use this only for a controlled test with permission to process the video.

## 1. Validate the model

From the repository root in Windows Command Prompt:

```cmd
check-ppe-model.cmd "D:\path\to\ppe-model.pt"
```

The checker must report `READY`. The model needs worker/person, helmet/hardhat, and vest/safety-vest labels.

## 2. Configure pilot mode

Open `backend\.env` and set:

```text
MODEL_PATH=D:\absolute\path\to\ppe-model.pt
DEMO_MODE=false
```

Never commit the model file, raw CCTV video, incident images, `.env`, or personal data.

## 3. Start the dashboard

```cmd
start-pilot.cmd
```

The pilot launcher checks that demo mode is disabled, then starts the local backend and frontend. The dashboard readiness panel should show whether the model file, vision dependencies, and at least one safety zone are ready.

## 4. Run one controlled video test

1. Create one rectangular safety zone.
2. Upload one short, authorised video under 100 MB.
3. Review every generated event as confirmed violation, false alarm, or unclear.
4. Download the CSV report.
5. Record the test conditions and manual ground truth in `docs/PILOT_METRICS_TEMPLATE.md`.

## Honest reporting rule

Do not report model accuracy, near-miss detection, multi-camera tracking, safety certification, or production readiness until the results are measured in a controlled pilot.
