from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.agents import (
    FlightResearchSchema,
    HotelResearchSchema,
    DestinationResearchSchema,
    WeatherResearchSchema,
    FoodResearchSchema,
    ActivityResearchSchema,
    ResearchSourceSchema,
    AgentRunResponse,
)
from app.schemas.budget import BudgetSchema
from app.schemas.itinerary import ItinerarySchema


class TripCreatePrompt(BaseModel):
    prompt: str = Field(..., min_length=5, description="Natural language trip description")


class TripCreateStructured(BaseModel):
    origin: Optional[str] = None
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_days: Optional[int] = 7
    travellers: Optional[int] = 1
    budget: Optional[float] = None
    currency: Optional[str] = "INR"
    travel_style: Optional[str] = "balanced"
    interests: Optional[List[str]] = []
    dietary_preferences: Optional[List[str]] = []
    accommodation_preferences: Optional[str] = "Boutique / 3-4 star"
    special_constraints: Optional[str] = None


class TripListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    origin: Optional[str] = None
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_days: int
    travellers: int
    budget: Optional[float] = None
    currency: str
    travel_style: Optional[str] = None
    status: str
    summary: Optional[str] = None
    created_at: datetime


class TripDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    origin: Optional[str] = None
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_days: int
    travellers: int
    budget: Optional[float] = None
    currency: str
    travel_style: Optional[str] = None
    interests: List[str] = []
    dietary_preferences: List[str] = []
    accommodation_preferences: Optional[str] = None
    status: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Associated nested components
    flight_research: Optional[FlightResearchSchema] = None
    hotel_research: Optional[HotelResearchSchema] = None
    destination_research: Optional[DestinationResearchSchema] = None
    weather_research: Optional[WeatherResearchSchema] = None
    food_research: Optional[FoodResearchSchema] = None
    activity_research: Optional[ActivityResearchSchema] = None
    budget_details: Optional[BudgetSchema] = None
    itinerary: Optional[ItinerarySchema] = None
    sources: List[ResearchSourceSchema] = []
    agent_runs: List[AgentRunResponse] = []
