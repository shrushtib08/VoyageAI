from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database.session import get_db
from app.models.research import ResearchSource
from app.models.trip import AgentRun, Trip
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/overview")
def admin_overview(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    del admin
    users = db.query(func.count(User.id)).scalar() or 0
    trips = db.query(func.count(Trip.id)).scalar() or 0
    sources = db.query(func.count(ResearchSource.id)).scalar() or 0
    runs = db.query(func.count(AgentRun.id)).scalar() or 0
    documents = 0
    if db.get_bind().dialect.name == "postgresql" and inspect(db.get_bind()).has_table("rag_documents"):
        try:
            documents = db.execute(text("SELECT COUNT(*) FROM rag_documents")).scalar() or 0
        except Exception:
            db.rollback()
            raise

    latest_users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .limit(10)
        .all()
    )
    latest_trips = (
        db.query(Trip)
        .order_by(Trip.created_at.desc())
        .limit(10)
        .all()
    )
    latest_runs = (
        db.query(AgentRun)
        .order_by(AgentRun.created_at.desc())
        .limit(10)
        .all()
    )
    return {
        "counts": {
            "users": users,
            "trips": trips,
            "agent_runs": runs,
            "research_sources": sources,
            "rag_documents": documents,
        },
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in latest_users
        ],
        "trips": [
            {
                "id": trip.id,
                "title": trip.title,
                "destination": trip.destination,
                "status": trip.status.value,
                "username": trip.user.username,
                "created_at": trip.created_at.isoformat() if trip.created_at else None,
            }
            for trip in latest_trips
        ],
        "agent_runs": [
            {
                "id": run.id,
                "trip_id": run.trip_id,
                "agent_name": run.agent_name,
                "status": run.status.value,
                "created_at": run.created_at.isoformat() if run.created_at else None,
                "duration_seconds": run.duration_seconds,
            }
            for run in latest_runs
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/me", response_model=UserResponse)
def admin_me(admin: User = Depends(get_current_admin)):
    return UserResponse.model_validate(admin)
