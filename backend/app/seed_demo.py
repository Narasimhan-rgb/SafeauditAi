"""Create clearly labelled local sample records for dashboard walkthroughs.

Run only on a local development database:
    python -m app.seed_demo
"""
from sqlalchemy import select

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import SafetyEvent, SafetyZone

DEMO_SOURCE = "safeaudit-local-demo"
DEMO_ZONE_NAME = "Demo Assembly Bay"


def seed_demo_data() -> int:
    if not settings.demo_mode:
        raise RuntimeError("DEMO_MODE is false. Set DEMO_MODE=true in backend/.env for local sample data.")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        zone = db.scalar(select(SafetyZone).where(SafetyZone.name == DEMO_ZONE_NAME))
        if zone is None:
            zone = SafetyZone(
                name=DEMO_ZONE_NAME,
                required_ppe="helmet,vest",
                coordinates="[80, 80, 500, 430]",
            )
            db.add(zone)

        existing_events = db.scalars(
            select(SafetyEvent).where(SafetyEvent.source_name == DEMO_SOURCE)
        ).all()
        if existing_events:
            db.commit()
            return 0

        db.add_all(
            [
                SafetyEvent(
                    event_type="ppe_non_compliance",
                    severity="high",
                    message="DEMO ONLY: Helmet not detected in the configured demo zone. Review required.",
                    source_name=DEMO_SOURCE,
                ),
                SafetyEvent(
                    event_type="ppe_non_compliance",
                    severity="medium",
                    message="DEMO ONLY: Safety vest not detected in the configured demo zone. Review required.",
                    source_name=DEMO_SOURCE,
                ),
            ]
        )
        db.commit()
        return 2
    finally:
        db.close()


def main() -> None:
    created = seed_demo_data()
    if created:
        print(f"Created {created} local demo events. Open the dashboard and mark review verdicts.")
    else:
        print("Demo data already exists. No new sample events were created.")


if __name__ == "__main__":
    main()
