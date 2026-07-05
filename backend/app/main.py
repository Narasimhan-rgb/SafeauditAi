import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
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


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "incident_images").mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

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
    """Temporary endpoint for testing the dashboard before model integration."""
    event = SafetyEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event_to_response(event)


@app.get(f"{settings.api_prefix}/events", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)) -> list[EventResponse]:
    events = db.scalars(select(SafetyEvent).order_by(SafetyEvent.created_at.desc())).all()
    return [event_to_response(event) for event in events]


@app.post(f"{settings.api_prefix}/analysis/video", response_model=AnalysisResponse)
async def analyze_video(file: UploadFile = File(...)) -> AnalysisResponse:
    """Validates the upload path; PPE inference is added after authorised model setup."""
    allowed_suffixes = {".mp4", ".avi", ".mov", ".mkv"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed_suffixes:
        raise HTTPException(status_code=415, detail="Upload MP4, AVI, MOV, or MKV video.")
    if not settings.model_path:
        raise HTTPException(
            status_code=503,
            detail=(
                "PPE model is not configured. Add an authorised custom model path in "
                "backend/.env before analysis."
            ),
        )

    return AnalysisResponse(
        status="queued",
        message="Video accepted. Full inference worker is the next build task.",
    )
