from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database.session import Base


class TripStatus(str, enum.Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    origin = Column(String(100), nullable=True)
    destination = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    duration_days = Column(Integer, default=7)
    travellers = Column(Integer, default=1)
    budget = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    travel_style = Column(String(50), default="balanced")
    interests = Column(JSON, default=list)
    dietary_preferences = Column(JSON, default=list)
    accommodation_preferences = Column(String(100), nullable=True)
    status = Column(SQLEnum(TripStatus), default=TripStatus.DRAFT, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="trips")
    request_details = relationship("TripRequest", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="trip", cascade="all, delete-orphan")
    flight_research = relationship("FlightResearch", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    hotel_research = relationship("HotelResearch", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    destination_research = relationship("DestinationResearch", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    weather_research = relationship("WeatherResearch", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    food_research = relationship("FoodResearch", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    activity_research = relationship("ActivityResearch", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    budget_details = relationship("Budget", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    itinerary = relationship("Itinerary", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    conversation = relationship("Conversation", back_populates="trip", uselist=False, cascade="all, delete-orphan")
    sources = relationship("ResearchSource", back_populates="trip", cascade="all, delete-orphan")


class TripRequest(Base):
    __tablename__ = "trip_requests"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    raw_prompt = Column(Text, nullable=False)
    structured_params = Column(JSON, default=dict)
    extracted_constraints = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="request_details")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)  # TravelManager, FlightAgent, etc.
    status = Column(SQLEnum(AgentRunStatus), default=AgentRunStatus.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    logs = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="agent_runs")
