from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import SafetyZone


def build_readiness(db: Session) -> dict[str, object]:
    """Return transparent MVP readiness information for the local dashboard.

    This endpoint does not load model weights or inspect any video. It only helps
    the builder verify prerequisites before starting a local test run.
    """

    configured_model_path = settings.model_path or ""
    model_configured = bool(configured_model_path)
    model_file_found = model_configured and Path(configured_model_path).is_file()

    try:
        import ultralytics  # noqa: F401

        vision_dependencies_ready = True
    except ImportError:
        vision_dependencies_ready = False

    zones_count = len(db.scalars(select(SafetyZone)).all())
    blockers: list[str] = []
    if not model_configured:
        blockers.append("Set MODEL_PATH in backend/.env to an authorised custom PPE model.")
    elif not model_file_found:
        blockers.append("The configured PPE model file cannot be found at MODEL_PATH.")
    if not vision_dependencies_ready:
        blockers.append("Install optional vision packages from requirements-vision.txt.")
    if zones_count == 0:
        blockers.append("Create at least one safety zone before analysing a test video.")

    return {
        "ready_for_test": len(blockers) == 0,
        "model_configured": model_configured,
        "model_file_found": model_file_found,
        "vision_dependencies_ready": vision_dependencies_ready,
        "configured_zones": zones_count,
        "demo_mode": settings.demo_mode,
        "blockers": blockers,
        "scope_note": "Phase 1 supports authorised local test videos, PPE compliance and configured zones only.",
        "demo_note": "Demo mode creates clearly labelled local sample events only; it does not use video analysis or a PPE model.",
    }
