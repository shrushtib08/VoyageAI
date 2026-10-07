import asyncio
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db, SessionLocal
from app.models.user import User
from app.models.trip import Trip, TripStatus
from app.schemas.trip import (
    TripCreatePrompt,
    TripCreateStructured,
    TripListItem,
    TripDetail,
)
from app.api.deps import get_current_user
from app.agents.orchestrator import orchestrator, MultiAgentOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["Trips"])


def _run_orchestrator_job(trip_id: int, raw_prompt: str, structured_input: Optional[dict]):
    """Background runner with its own database session."""
    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            orchestrator.plan_trip(
                trip_id=trip_id,
                raw_prompt=raw_prompt,
                structured_input=structured_input,
                db=db
            )
        )
        loop.close()
    except Exception as e:
        logger.error(f"Background orchestrator failure for trip {trip_id}: {e}", exc_info=True)
    finally:
        db.close()


@router.post("/plan-prompt", response_model=TripListItem, status_code=status.HTTP_201_CREATED)
def plan_trip_from_prompt(
    payload: TripCreatePrompt,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create initial Trip placeholder
    trip = Trip(
        user_id=current_user.id,
        title="Synthesizing Itinerary...",
        destination="Processing...",
        status=TripStatus.PLANNING,
        summary="VoyageAI Multi-Agent system is planning your journey."
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # Launch multi-agent execution in background
    background_tasks.add_task(
        _run_orchestrator_job,
        trip.id,
        payload.prompt,
        None
    )

    return TripListItem.model_validate(trip)


@router.post("/plan-structured", response_model=TripListItem, status_code=status.HTTP_201_CREATED)
def plan_trip_structured(
    payload: TripCreateStructured,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Formulate natural prompt representation
    constraints_str = f" Special constraints: {payload.special_constraints}." if payload.special_constraints else ""
    dietary_str = f" Dietary preferences: {', '.join(payload.dietary_preferences)}." if payload.dietary_preferences else ""
    interests_str = f" Interests: {', '.join(payload.interests)}." if payload.interests else ""

    generated_prompt = (
        f"Plan a {payload.duration_days}-day trip to {payload.destination} "
        f"{f'from {payload.origin} ' if payload.origin else ''}"
        f"for {payload.travellers} traveler(s) with style '{payload.travel_style}'. "
        f"{f'Budget: {payload.currency} {payload.budget:,.0f}. ' if payload.budget else ''}"
        f"{interests_str}{dietary_str}{constraints_str}"
    )

    trip = Trip(
        user_id=current_user.id,
        title=f"{payload.duration_days}-Day Trip to {payload.destination}",
        origin=payload.origin,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        duration_days=payload.duration_days or 7,
        travellers=payload.travellers or 1,
        budget=payload.budget,
        currency=payload.currency or "INR",
        travel_style=payload.travel_style or "balanced",
        interests=payload.interests or [],
        dietary_preferences=payload.dietary_preferences or [],
        accommodation_preferences=payload.accommodation_preferences,
        status=TripStatus.PLANNING,
        summary="VoyageAI Multi-Agent system is planning your journey."
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    background_tasks.add_task(
        _run_orchestrator_job,
        trip.id,
        generated_prompt,
        payload.model_dump()
    )

    return TripListItem.model_validate(trip)


@router.get("", response_model=List[TripListItem])
def list_trips(
    search: Optional[str] = Query(None, description="Search by title, destination, or origin"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Trip).filter(Trip.user_id == current_user.id)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Trip.title.ilike(search_filter),
                Trip.destination.ilike(search_filter),
                Trip.origin.ilike(search_filter)
            )
        )
    trips = query.order_by(Trip.created_at.desc()).all()
    return [TripListItem.model_validate(t) for t in trips]


@router.get("/{trip_id}", response_model=TripDetail)
def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You do not own this trip.")

    return TripDetail.model_validate(trip)


@router.get("/{trip_id}/progress")
def get_trip_progress(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    prog = MultiAgentOrchestrator.get_progress(trip_id)
    if prog:
        return prog

    # If completed or no active in-memory progress
    return {
        "trip_id": trip_id,
        "current_stage": "Complete" if trip.status == TripStatus.COMPLETED else trip.status.value,
        "progress_percentage": 100 if trip.status == TripStatus.COMPLETED else 0,
        "status": trip.status.value,
        "message": "Trip finalized" if trip.status == TripStatus.COMPLETED else "Pending start",
        "agents": {run.agent_name: {"status": run.status.value, "message": run.logs or ""} for run in trip.agent_runs}
    }


@router.get("/{trip_id}/stream")
async def stream_trip_progress(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """Server-Sent Events endpoint streaming live agent execution updates."""
    async def event_generator():
        last_pct = -1
        retry_count = 0
        while True:
            prog = MultiAgentOrchestrator.get_progress(trip_id)
            if prog:
                yield f"data: {json.dumps(prog)}\n\n"
                if prog.get("status") in ["completed", "failed"]:
                    break
            else:
                # Query DB status
                curr_trip = db.query(Trip).filter(Trip.id == trip_id).first()
                if curr_trip and curr_trip.status in [TripStatus.COMPLETED, TripStatus.FAILED]:
                    fallback_data = {
                        "trip_id": trip_id,
                        "status": curr_trip.status.value,
                        "progress_percentage": 100 if curr_trip.status == TripStatus.COMPLETED else 0,
                        "message": "Trip processing concluded."
                    }
                    yield f"data: {json.dumps(fallback_data)}\n\n"
                    break
                retry_count += 1
                if retry_count > 60:
                    break
            await asyncio.sleep(0.7)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    db.delete(trip)
    db.commit()
    return None
