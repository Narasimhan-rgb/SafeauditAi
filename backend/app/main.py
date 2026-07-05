import csv
import io
import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import SafetyEvent, SafetyZone
from app.schemas import (
    AnalysisResponse,
    EventCreate,
    EventResponse,
    ZoneCreate,
    ZoneResponse,
)
from app.services.ppe_detector import ModelConfigurationError, PPEDetector
from app.services.video_analysis import analyse_video


incident_directory = settings.data_dir / "incident_images"
incident_directory.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "uploads").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)
app.mount("/evidence", StaticFiles(directory=incident_directory), name="evidence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def zone_to_response(zone: SafetyZone) -> ZoneResponse:
    return ZoneResponse(
        id=zone.id,
        name=zone.name,
        required_ppe=[item for item in zone.required_ppe.split(",") if item],
        coordinates=json.loads(zone.coordinates),
        created_at=zone.created_at,
    )


def event_to_response(event: SafetyEvent) -> EventResponse:
    return EventResponse(
        id=event.id,
        event_type=event.event_type,
        severity=event.severity,
        message=event.message,
        source_name=event.source_name,
        evidence_path=event.evidence_path,
        created_at=event.created_at,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.post(f"{settings.api_prefix}/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)) -> ZoneResponse:
    existing = db.scalar(select(SafetyZone).where(SafetyZone.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="A zone with this name already exists.")

    zone = SafetyZone(
        name=payload.name,
        required_ppe=",".join(payload.required_ppe),
        coordinates=json.dumps(payload.coordinates),
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone_to_response(zone)


@app.get(f"{settings.api_prefix}/zones", response_model=list[ZoneResponse])
def list_zones(db: Session = Depends(get_db)) -> list[ZoneResponse]:
    zones = db.scalars(select(SafetyZone).order_by(SafetyZone.created_at.desc())).all()
    return [zone_to_response(zone) for zone in zones]


@app.post(f"{settings.api_prefix}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_manual_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventResponse:
    """Temporary endpoint for dashboard verification before model integration."""
    event = SafetyEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event_to_response(event)


@app.get(f"{settings.api_prefix}/events", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)) -> list[EventResponse]:
    events = db.scalars(select(SafetyEvent).order_by(SafetyEvent.created_at.desc())).all()
    return [event_to_response(event) for event in events]


@app.get(f"{settings.api_prefix}/metrics")
def safety_metrics(db: Session = Depends(get_db)) -> dict[str, int]:
    """Small dashboard summary for local prototype review."""
    events = db.scalars(select(SafetyEvent)).all()
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=24)
    zones_count = len(db.scalars(select(SafetyZone)).all())
    return {
        "total_events": len(events),
        "high_risk_events": sum(event.severity == "high" for event in events),
        "events_last_24h": sum(event.created_at >= cutoff for event in events),
        "configured_zones": zones_count,
    }


@app.get(f"{settings.api_prefix}/reports/events.csv")
def export_events_csv(db: Session = Depends(get_db)) -> Response:
    """Exports a local review report. It contains metadata only, never raw video."""
    events = db.scalars(select(SafetyEvent).order_by(SafetyEvent.created_at.desc())).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["event_id", "created_at", "event_type", "severity", "message", "source_name", "evidence_path"])
    for event in events:
        writer.writerow([
            event.id,
            event.created_at.isoformat(),
            event.event_type,
            event.severity,
            event.message,
            event.source_name or "",
            event.evidence_path or "",
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=safeaudit-events.csv"},
    )


@app.post(f"{settings.api_prefix}/analysis/video", response_model=AnalysisResponse)
async def analyze_video(file: UploadFile = File(...), db: Session = Depends(get_db)) -> AnalysisResponse:
    """Analyse one local test video and retain only violation evidence images.

    The endpoint processes synchronously for the MVP. Use short, authorised test
    clips only; a production version requires a background worker and review flow.
    """

    allowed_suffixes = {".mp4", ".avi", ".mov", ".mkv"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed_suffixes:
        raise HTTPException(status_code=415, detail="Upload MP4, AVI, MOV, or MKV video.")
    if not settings.model_path:
        raise HTTPException(
            status_code=503,
            detail=(
                "PPE model is not configured. Add an authorised custom model path in "
                "backend/.env and install requirements-vision.txt before analysis."
            ),
        )

    zones = db.scalars(select(SafetyZone)).all()
    if not zones:
        raise HTTPException(
            status_code=422,
            detail="Create at least one configured safety zone before analysing a video.",
        )

    upload_path = settings.data_dir / "uploads" / f"upload_{Path(file.filename).name}"
    max_upload_bytes = 100 * 1024 * 1024
    bytes_written = 0

    try:
        with upload_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                bytes_written += len(chunk)
                if bytes_written > max_upload_bytes:
                    raise HTTPException(status_code=413, detail="Video must be smaller than 100 MB for the MVP.")
                destination.write(chunk)

        detector = PPEDetector(settings.model_path)
        result = analyse_video(upload_path, detector, zones, incident_directory)

        for generated in result.events:
            db.add(
                SafetyEvent(
                    event_type=generated.event_type,
                    severity=generated.severity,
                    message=generated.message,
                    source_name=file.filename,
                    evidence_path=generated.evidence_path,
                )
            )
        db.commit()

        return AnalysisResponse(
            status="completed",
            message="Analysis finished. Review generated events before taking any safety action.",
            processed_frames=result.processed_frames,
            events_created=len(result.events),
        )
    except ModelConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        if upload_path.exists():
            upload_path.unlink()
        await file.close()
