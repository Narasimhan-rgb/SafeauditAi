from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class ZoneCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    required_ppe: list[str] = Field(default_factory=lambda: ["helmet", "vest"])
    coordinates: list[int] = Field(
        min_length=4,
        max_length=4,
        description="Rectangle: [x1, y1, x2, y2] in video-frame pixels.",
    )

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Zone name must contain at least two visible characters.")
        return cleaned

    @field_validator("required_ppe")
    @classmethod
    def validate_required_ppe(cls, values: list[str]) -> list[str]:
        supported = {"helmet", "vest"}
        normalised = list(dict.fromkeys(value.strip().lower() for value in values if value.strip()))
        if not normalised:
            raise ValueError("Select at least one required PPE item.")
        unsupported = set(normalised) - supported
        if unsupported:
            raise ValueError(f"Unsupported PPE items: {', '.join(sorted(unsupported))}.")
        return normalised

    @model_validator(mode="after")
    def validate_rectangle(self):
        x1, y1, x2, y2 = self.coordinates
        if min(self.coordinates) < 0:
            raise ValueError("Zone coordinates cannot be negative.")
        if x2 <= x1 or y2 <= y1:
            raise ValueError("Zone coordinates must follow x1 < x2 and y1 < y2.")
        return self


class ZoneResponse(BaseModel):
    id: int
    name: str
    required_ppe: list[str]
    coordinates: list[int]
    created_at: datetime


class EventCreate(BaseModel):
    event_type: str = Field(default="ppe_non_compliance", max_length=80)
    severity: str = Field(default="medium", pattern="^(low|medium|high)$")
    message: str = Field(min_length=3, max_length=500)
    source_name: str | None = Field(default=None, max_length=255)


class EventResponse(EventCreate):
    id: int
    evidence_path: str | None = None
    created_at: datetime


class EventReviewCreate(BaseModel):
    verdict: str = Field(pattern="^(confirmed_violation|false_alarm|unclear)$")
    reviewer_note: str | None = Field(default=None, max_length=500)


class EventReviewResponse(EventReviewCreate):
    id: int
    event_id: int
    reviewed_at: datetime


class AnalysisResponse(BaseModel):
    status: str
    message: str
    processed_frames: int = 0
    events_created: int = 0


class EvaluationSummary(BaseModel):
    real_events: int
    demo_events: int
    reviewed_real_events: int
    confirmed_violations: int
    false_alarms: int
    unclear_events: int
    precision: float | None = None
    review_rate: float
    ready_for_reporting: bool
    note: str
