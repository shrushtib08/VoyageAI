from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    flights_cost = Column(Float, default=0.0)
    accommodation_cost = Column(Float, default=0.0)
    food_cost = Column(Float, default=0.0)
    local_transport_cost = Column(Float, default=0.0)
    activities_cost = Column(Float, default=0.0)
    misc_cost = Column(Float, default=0.0)
    emergency_buffer = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)
    total_budget = Column(Float, default=0.0)
    per_person_cost = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    is_estimate = Column(Boolean, default=True)
    category_breakdown = Column(JSON, default=dict)
    budget_advice = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="budget_details")
