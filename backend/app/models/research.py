from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class FlightResearch(Base):
    __tablename__ = "flight_researches"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    origin_airport = Column(String(50), nullable=True)
    destination_airport = Column(String(50), nullable=True)
    route_summary = Column(Text, nullable=True)
    direct_options = Column(JSON, default=list)
    connecting_options = Column(JSON, default=list)
    airlines = Column(JSON, default=list)
    fare_range_low = Column(Float, nullable=True)
    fare_range_high = Column(Float, nullable=True)
    estimated_duration_hours = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    is_live_data = Column(Boolean, default=False)
    api_status_note = Column(String(255), nullable=True)
    source_citations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="flight_research")


class HotelResearch(Base):
    __tablename__ = "hotel_researches"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    recommendations = Column(JSON, default=list)
    budget_category = Column(String(50), nullable=True)
    avg_nightly_price = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    is_live_data = Column(Boolean, default=False)
    api_status_note = Column(String(255), nullable=True)
    source_citations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="hotel_research")


class DestinationResearch(Base):
    __tablename__ = "destination_researches"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    major_attractions = Column(JSON, default=list)
    cultural_sites = Column(JSON, default=list)
    lesser_known_gems = Column(JSON, default=list)
    neighborhoods = Column(JSON, default=list)
    local_tips = Column(JSON, default=list)
    practical_info = Column(JSON, default=dict)
    source_citations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="destination_research")


class WeatherResearch(Base):
    __tablename__ = "weather_researches"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    destination = Column(String(100), nullable=False)
    season_summary = Column(String(255), nullable=True)
    avg_temp_min = Column(Float, nullable=True)
    avg_temp_max = Column(Float, nullable=True)
    precipitation_probability = Column(Float, nullable=True)
    weather_conditions = Column(String(255), nullable=True)
    travel_advice = Column(Text, nullable=True)
    packing_suggestions = Column(JSON, default=list)
    is_live_forecast = Column(Boolean, default=False)
    api_status_note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="weather_research")


class FoodResearch(Base):
    __tablename__ = "food_researches"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    local_dishes = Column(JSON, default=list)
    popular_food_areas = Column(JSON, default=list)
    recommended_spots = Column(JSON, default=list)
    street_food = Column(JSON, default=list)
    dietary_suitability = Column(JSON, default=dict)  # vegetarian, vegan, halal, etc.
    price_level_summary = Column(String(100), nullable=True)
    source_citations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="food_research")


class ActivityResearch(Base):
    __tablename__ = "activity_researches"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, unique=True)
    ranked_activities = Column(JSON, default=list)  # list of objects with rank, title, category, description, duration, cost
    source_citations = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="activity_research")


class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
    snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trip = relationship("Trip", back_populates="sources")
