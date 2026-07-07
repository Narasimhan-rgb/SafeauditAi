from datetime import datetime

from pydantic import BaseModel, Field


class ZoneCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    required_ppe: list[str] = Field(default_factory=lambda: ["helmet", "vest"])
    coordinates: list[int] = Field(
        min_length=4,
        max_length=4,
        description="Rectangle: [x1, y1, x2, y2] in video-frame pixels.",
    )


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
