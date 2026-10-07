from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class BudgetCategoryItem(BaseModel):
    category: str
    amount: float
    percentage: float
    notes: Optional[str] = None


class BudgetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    trip_id: int
    flights_cost: float
    accommodation_cost: float
    food_cost: float
    local_transport_cost: float
    activities_cost: float
    misc_cost: float
    emergency_buffer: float
    subtotal: float
    total_budget: float
    per_person_cost: float
    currency: str = "INR"
    is_estimate: bool = True
    category_breakdown: Dict[str, Any] = {}
    budget_advice: Optional[str] = None


class BudgetUpdateSchema(BaseModel):
    flights_cost: Optional[float] = None
    accommodation_cost: Optional[float] = None
    food_cost: Optional[float] = None
    local_transport_cost: Optional[float] = None
    activities_cost: Optional[float] = None
    misc_cost: Optional[float] = None
    emergency_buffer: Optional[float] = None
    currency: Optional[str] = None
