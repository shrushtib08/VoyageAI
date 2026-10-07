from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class TimeBlock(BaseModel):
    time: str
    activity: str
    location: str
    transport: Optional[str] = None
    estimated_cost: Optional[float] = 0.0
    practical_tip: Optional[str] = None
    source: Optional[str] = None


class ItineraryDaySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    day_number: int
    date_str: Optional[str] = None
    theme: str
    morning: Dict[str, Any] = {}
    afternoon: Dict[str, Any] = {}
    evening: Dict[str, Any] = {}
    attractions: List[str] = []
    food_suggestions: List[str] = []
    transport_notes: Optional[str] = None
    estimated_daily_spend: float = 0.0
    practical_notes: Optional[str] = None


class ItinerarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    trip_id: int
    total_days: int
    title: Optional[str] = None
    overview: Optional[str] = None
    validation_status: str = "VALID"
    critique_notes: Optional[str] = None
    validation_flags: List[str] = []
    revision_count: int = 0
    practical_tips: List[str] = []
    days: List[ItineraryDaySchema] = []
