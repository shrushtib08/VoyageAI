from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    total_days = Column(Integer, default=7)
    title = Column(String(255), nullable=True)
    overview = Column(Text, nullable=True)
    validation_status = Column(String(50), default="VALID")  # VALID, NEEDS_REVISION, PENDING
    critique_notes = Column(Text, nullable=True)
    validation_flags = Column(JSON, default=list)
    revision_count = Column(Integer, default=0)
    practical_tips = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="itinerary")
    days = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan", order_by="ItineraryDay.day_number")


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    date_str = Column(String(50), nullable=True)
    theme = Column(String(255), nullable=False)
    morning = Column(JSON, default=dict)      # {time, activity, location, transport, cost, tips}
    afternoon = Column(JSON, default=dict)    # {time, activity, location, transport, cost, tips}
    evening = Column(JSON, default=dict)      # {time, activity, location, transport, cost, tips}
    attractions = Column(JSON, default=list)
    food_suggestions = Column(JSON, default=list)
    transport_notes = Column(Text, nullable=True)
    estimated_daily_spend = Column(Float, default=0.0)
    practical_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    itinerary = relationship("Itinerary", back_populates="days")
