import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.trip import Trip
from app.models.chat import Conversation, Message
from app.models.itinerary import Itinerary, ItineraryDay
from app.models.budget import Budget
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ConversationResponse
from app.api.deps import get_current_user
from app.rag.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips/{trip_id}/chat", tags=["Trip Follow-up Chat"])


@router.get("", response_model=ConversationResponse)
def get_trip_conversation(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    conv = db.query(Conversation).filter(Conversation.trip_id == trip_id).first()
    if not conv:
        conv = Conversation(trip_id=trip_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    return ConversationResponse.model_validate(conv)


@router.post("", response_model=ChatMessageResponse)
async def post_followup_message(
    trip_id: int,
    chat_req: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    conv = db.query(Conversation).filter(Conversation.trip_id == trip_id).first()
    if not conv:
        conv = Conversation(trip_id=trip_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 1. Save user message
    user_msg = Message(
        conversation_id=conv.id,
        sender="user",
        content=chat_req.message.strip()
    )
    db.add(user_msg)
    db.commit()

    # 2. Build context from existing trip details
    itin = trip.itinerary
    budget_rec = trip.budget_details
    days_data = []
    if itin:
        for d in itin.days:
            days_data.append({
                "day_number": d.day_number,
                "theme": d.theme,
                "morning": d.morning.get("activity") if isinstance(d.morning, dict) else d.morning,
                "afternoon": d.afternoon.get("activity") if isinstance(d.afternoon, dict) else d.afternoon,
                "evening": d.evening.get("activity") if isinstance(d.evening, dict) else d.evening,
                "estimated_daily_spend": d.estimated_daily_spend,
            })

    trip_context_str = (
        f"Trip: {trip.title} ({trip.duration_days} days to {trip.destination})\n"
        f"Travelers: {trip.travellers}, Budget: {trip.currency} {trip.budget}\n"
        f"Current Estimated Budget: {trip.currency} {budget_rec.total_budget if budget_rec else 'N/A'}\n"
        f"Interests: {trip.interests}\n"
        f"Dietary: {trip.dietary_preferences}\n"
        f"Itinerary Days: {days_data}\n"
    )

    # Prior messages (last 6)
    history_msgs = db.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.desc()).limit(6).all()
    history_msgs.reverse()
    history_str = "\n".join([f"{m.sender.upper()}: {m.content}" for m in history_msgs])

    # 3. Answer from retrieved evidence, falling back to web research or abstaining.
    try:
        rag_answer = await rag_service.answer(
            query=f"{trip.destination}: {chat_req.message}",
            destination=trip.destination,
            trip_context=f"{trip_context_str}\nCONVERSATION HISTORY:\n{history_str}",
            db=db,
        )
    except Exception as exc:
        logger.exception("Grounded trip chat response failed.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to generate a grounded answer from retrieved travel sources.",
        ) from exc
    reply_text = rag_answer["answer"]
    actions_taken = {
        "sources": rag_answer["sources"],
        "source_types": rag_answer["source_types"],
        "grounded": rag_answer["grounded"],
    }

    # 4. Save assistant response
    ai_msg = Message(
        conversation_id=conv.id,
        sender="assistant",
        content=reply_text,
        actions_taken=actions_taken
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ChatMessageResponse.model_validate(ai_msg)
