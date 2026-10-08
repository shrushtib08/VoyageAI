from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ResearchSourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_name: str
    title: str
    source_type: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class FlightOption(BaseModel):
    airline: str
    flight_number: Optional[str] = None
    departure_airport: str
    arrival_airport: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration_hours: Optional[float] = None
    stops: int = 0
    estimated_price: Optional[float] = None
    is_live_data: bool = False
    notes: Optional[str] = None


class FlightResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    origin_airport: Optional[str] = None
    destination_airport: Optional[str] = None
    route_summary: Optional[str] = None
    direct_options: List[FlightOption] = []
    connecting_options: List[FlightOption] = []
    airlines: List[str] = []
    fare_range_low: Optional[float] = None
    fare_range_high: Optional[float] = None
    estimated_duration_hours: Optional[float] = None
    currency: str = "INR"
    is_live_data: bool = False
    api_status_note: Optional[str] = None
    source_citations: List[ResearchSourceSchema] = []


class HotelItem(BaseModel):
    name: str
    area: str
    approx_price_per_night: float
    currency: str = "INR"
    rating: Optional[float] = None
    description: str
    source: Optional[str] = None
    recommendation_reason: Optional[str] = None
    amenities: List[str] = []


class HotelResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendations: List[HotelItem] = []
    budget_category: Optional[str] = None
    avg_nightly_price: Optional[float] = None
    currency: str = "INR"
    is_live_data: bool = False
    api_status_note: Optional[str] = None
    source_citations: List[ResearchSourceSchema] = []


class AttractionItem(BaseModel):
    name: str
    category: str
    description: str
    approx_visit_time_hours: float
    opening_hours: Optional[str] = None
    entry_fee: Optional[float] = None
    tips: Optional[str] = None
    source: Optional[str] = None


class DestinationResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    major_attractions: List[AttractionItem] = []
    cultural_sites: List[AttractionItem] = []
    lesser_known_gems: List[AttractionItem] = []
    neighborhoods: List[Dict[str, Any]] = []
    local_tips: List[str] = []
    practical_info: Dict[str, Any] = {}
    source_citations: List[ResearchSourceSchema] = []


class WeatherResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    destination: str
    season_summary: Optional[str] = None
    avg_temp_min: Optional[float] = None
    avg_temp_max: Optional[float] = None
    precipitation_probability: Optional[float] = None
    weather_conditions: Optional[str] = None
    travel_advice: Optional[str] = None
    packing_suggestions: List[str] = []
    is_live_forecast: bool = False
    api_status_note: Optional[str] = None


class FoodSpotItem(BaseModel):
    name: str
    area: str
    specialty: str
    price_level: str
    dietary_suitability: List[str] = []
    description: Optional[str] = None
    source: Optional[str] = None


class FoodResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    local_dishes: List[Dict[str, Any]] = []
    popular_food_areas: List[str] = []
    recommended_spots: List[FoodSpotItem] = []
    street_food: List[Dict[str, Any]] = []
    dietary_suitability: Dict[str, Any] = {}
    price_level_summary: Optional[str] = None
    source_citations: List[ResearchSourceSchema] = []


class ActivityItem(BaseModel):
    rank: int
    title: str
    category: str
    description: str
    estimated_duration_hours: float
    estimated_cost: float
    best_time_of_day: Optional[str] = "Morning"
    source: Optional[str] = None


class ActivityResearchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ranked_activities: List[ActivityItem] = []
    source_citations: List[ResearchSourceSchema] = []


class AgentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    agent_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    logs: Optional[str] = None
    output_summary: Optional[str] = None


class CriticValidationResult(BaseModel):
    status: str = Field(..., description="'VALID' or 'NEEDS_REVISION'")
    score: Optional[int] = Field(None, description="Quality score 1-100")
    critique_notes: str
    issues_found: List[str] = []
    revision_suggestions: List[str] = []
