from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from app.models import SafetyZone
from app.services.ppe_detector import Detection, PPEDetector, missing_ppe_for_person


@dataclass(frozen=True)
class GeneratedSafetyEvent:
    event_type: str
    severity: str
    message: str
    evidence_path: str


@dataclass(frozen=True)
class VideoAnalysisResult:
    processed_frames: int
    events: list[GeneratedSafetyEvent]


def point_in_rectangle(point: tuple[int, int], coordinates: list[int]) -> bool:
    x1, y1, x2, y2 = coordinates
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))
    return left <= point[0] <= right and top <= point[1] <= bottom


def _save_evidence(frame, zone_name: str, missing_items: list[str], evidence_dir: Path) -> str:
    import cv2

    evidence_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{zone_name.replace(' ', '_')}.jpg"
    output_path = evidence_dir / filename
    annotation = f"Missing {', '.join(missing_items)} in {zone_name}"
    cv2.putText(frame, annotation, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    cv2.imwrite(str(output_path), frame)
    return f"/evidence/{filename}"


def _draw_zone(frame, zone: SafetyZone) -> None:
    import cv2

    x1, y1, x2, y2 = json.loads(zone.coordinates)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
    cv2.putText(frame, zone.name, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)


def analyse_video(
    video_path: Path,
    detector: PPEDetector,
    zones: list[SafetyZone],
    evidence_dir: Path,
    sample_every_n_frames: int = 15,
) -> VideoAnalysisResult:
    """Runs a simple local Phase 1 analysis and emits one event per zone/PPE combination.

    This is intentionally a limited MVP: it has no person tracking, multi-camera
    orchestration, or safety certification claim.
    """

    import cv2

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError("Unable to open the uploaded video.")

    generated_events: list[GeneratedSafetyEvent] = []
    emitted_fingerprints: set[str] = set()
    frame_number = 0
    processed_frames = 0

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            frame_number += 1
            if frame_number % sample_every_n_frames != 0:
                continue

            processed_frames += 1
            detections = detector.infer(frame)
            people = [item for item in detections if item.label == "person"]
            if not people:
                continue

            for zone in zones:
                coordinates = json.loads(zone.coordinates)
                required_ppe = [item for item in zone.required_ppe.split(",") if item]
                for person in people:
                    foot_point = ((person.x1 + person.x2) // 2, person.y2)
                    if not point_in_rectangle(foot_point, coordinates):
                        continue

                    missing_items = missing_ppe_for_person(person, detections, required_ppe)
                    if not missing_items:
                        continue

                    fingerprint = f"{zone.id}:{','.join(sorted(missing_items))}"
                    if fingerprint in emitted_fingerprints:
                        continue
                    emitted_fingerprints.add(fingerprint)

                    evidence_frame = frame.copy()
                    _draw_zone(evidence_frame, zone)
                    evidence_path = _save_evidence(evidence_frame, zone.name, missing_items, evidence_dir)
                    severity = "high" if "helmet" in missing_items or len(missing_items) > 1 else "medium"
                    generated_events.append(
                        GeneratedSafetyEvent(
                            event_type="ppe_non_compliance",
                            severity=severity,
                            message=(
                                f"Missing {', '.join(missing_items)} in configured zone '{zone.name}'. "
                                "Review the event evidence before taking action."
                            ),
                            evidence_path=evidence_path,
                        )
                    )
    finally:
        capture.release()

    return VideoAnalysisResult(processed_frames=processed_frames, events=generated_events)
