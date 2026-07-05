# Run SafeAudit AI locally

## 1. Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs` to test the API and `http://127.0.0.1:8000/health` for service status.

## 2. Dashboard

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite address, normally `http://127.0.0.1:5173`.

## 3. Enable the PPE video path

The dashboard, zone API, and event log run without a vision model. For video analysis, install the optional dependencies:

```powershell
cd backend
pip install -r requirements-vision.txt
```

Then set an authorised model path in `backend/.env`:

```text
MODEL_PATH=path/to/your/ppe-model.pt
```

The model must expose exactly these labels: `person`, `helmet`, and `vest`.

## Demo sequence

1. Start backend and dashboard.
2. Save one rectangular safety zone through the dashboard.
3. Select a short authorised test clip.
4. Run local analysis.
5. Review the generated event and evidence image in the dashboard.

## Current status

This is a local prototype. It processes one short video synchronously and retains event evidence images only. It does not claim multi-camera support, validated near-miss detection, safety certification, or production accuracy.
