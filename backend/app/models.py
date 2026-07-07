from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SafetyZone(Base):
    __tablename__ = "safety_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    required_ppe: Mapped[str] = mapped_column(String(120), default="helmet,vest", nullable=False)
    coordinates: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class SafetyEvent(Base):
    __tablename__ = "safety_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class SafetyEventReview(Base):
    """Manual review record for a model-generated safety event.

    A separate table keeps the original detection event immutable while allowing
    a supervisor to document whether the result was confirmed, a false alarm,
    or still unclear during the prototype pilot.
    """

    __tablename__ = "safety_event_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
