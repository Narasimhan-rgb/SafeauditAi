from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ModelConfigurationError(RuntimeError):
    """Raised when the local PPE model cannot support the MVP labels."""


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def center(self) -> tuple[int, int]:
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)


class PPEDetector:
    """Adapter for an authorised custom model with person, helmet and vest labels.

    The package imports are intentionally local so the core API can still run
    without vision dependencies until a model is configured.
    """

    required_labels = {"person", "helmet", "vest"}

    def __init__(self, model_path: str):
        path = Path(model_path)
        if not path.is_file():
            raise ModelConfigurationError("Configured PPE model file was not found.")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ModelConfigurationError(
                "Install optional vision dependencies with: pip install -r requirements-vision.txt"
            ) from exc

        self.model = YOLO(str(path))
        raw_names = self.model.names
        self.class_names = {
            int(index): str(name).strip().lower()
            for index, name in (raw_names.items() if isinstance(raw_names, dict) else enumerate(raw_names))
        }
        model_labels = set(self.class_names.values())
        missing = self.required_labels - model_labels
        if missing:
            raise ModelConfigurationError(
                "The custom model must contain labels person, helmet and vest. "
                f"Missing: {', '.join(sorted(missing))}."
            )

    def infer(self, frame) -> list[Detection]:
        result = self.model.predict(source=frame, conf=0.35, imgsz=640, verbose=False)[0]
        detections: list[Detection] = []
        if result.boxes is None:
            return detections

        for box in result.boxes:
            class_id = int(box.cls[0].item())
            label = self.class_names.get(class_id)
            if label not in self.required_labels:
                continue
            x1, y1, x2, y2 = (int(value) for value in box.xyxy[0].tolist())
            detections.append(
                Detection(
                    label=label,
                    confidence=float(box.conf[0].item()),
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                )
            )
        return detections


def missing_ppe_for_person(person: Detection, detections: list[Detection], required_ppe: list[str]) -> list[str]:
    """Associates PPE with a person by checking its centre within the person box.

    This simple, explainable association is suitable for a Phase 1 single-camera
    prototype. It must be validated before any field deployment.
    """

    width = max(person.x2 - person.x1, 1)
    height = max(person.y2 - person.y1, 1)
    missing: list[str] = []

    for item in required_ppe:
        item_found = False
        for detection in detections:
            if detection.label != item:
                continue
            center_x, center_y = detection.center
            within_person = (
                person.x1 - int(width * 0.1) <= center_x <= person.x2 + int(width * 0.1)
                and person.y1 <= center_y <= person.y2
            )
            if not within_person:
                continue

            if item == "helmet":
                item_found = person.y1 - int(height * 0.15) <= center_y <= person.y1 + int(height * 0.42)
            elif item == "vest":
                item_found = person.y1 + int(height * 0.18) <= center_y <= person.y1 + int(height * 0.9)
            else:
                item_found = True

            if item_found:
                break

        if not item_found:
            missing.append(item)

    return missing
