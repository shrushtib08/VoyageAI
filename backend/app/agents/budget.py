import logging
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class BudgetAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="BudgetAgent",
            role="Financial & Resource Allocation Strategist",
            description="Synthesizes estimated expenditures across Flights, Accommodation, Dining, Transit, Activities, Miscellaneous, and Emergency Reserves with multi-currency support."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        target_budget = context.get("budget")
        currency = context.get("currency", "INR")
        travellers = context.get("travellers", 1)
        duration_days = context.get("duration_days", 7)
        nights = max(1, duration_days - 1)

        flight_data = context.get("flight_research", {})
        hotel_data = context.get("hotel_research", {})
        activity_data = context.get("activity_research", {})

        # Compute Flights Cost
        flight_low = flight_data.get("fare_range_low")
        flight_high = flight_data.get("fare_range_high")
        if flight_low and flight_high:
            avg_flight_pp = (flight_low + flight_high) / 2.0
        elif flight_low:
            avg_flight_pp = flight_low
        else:
            avg_flight_pp = 35000.0 if currency == "INR" else 450.0
        flights_cost = round(avg_flight_pp * travellers, 2)

        # Compute Accommodation Cost
        avg_nightly = hotel_data.get("avg_nightly_price") or (5500.0 if currency == "INR" else 75.0)
        # 1-2 people usually share 1 room; 3-4 share 2 rooms
        rooms_needed = max(1, (travellers + 1) // 2)
        accommodation_cost = round(avg_nightly * nights * rooms_needed, 2)

        # Compute Food Cost (approx per person per day)
        daily_food_pp = 1500.0 if currency == "INR" else 35.0
        food_cost = round(daily_food_pp * duration_days * travellers, 2)

        # Compute Local Transit Cost (metro cards, cabs, transfers)
        daily_transit_pp = 600.0 if currency == "INR" else 15.0
        local_transport_cost = round(daily_transit_pp * duration_days * travellers, 2)

        # Compute Activities Cost
        activities_list = activity_data.get("ranked_activities", [])
        total_act_sum = sum(a.get("estimated_cost", 0.0) for a in activities_list[:5])
        if total_act_sum == 0:
            total_act_sum = (3500.0 if currency == "INR" else 50.0)
        activities_cost = round(total_act_sum * travellers, 2)

        # Miscellaneous (souvenirs, SIM card, tipping, entrance fees)
        misc_cost = round((3000.0 if currency == "INR" else 40.0) * travellers, 2)

        # Subtotal
        subtotal = round(flights_cost + accommodation_cost + food_cost + local_transport_cost + activities_cost + misc_cost, 2)

        # Emergency Buffer (7% of subtotal)
        emergency_buffer = round(subtotal * 0.07, 2)

        # Total
        total_budget = round(subtotal + emergency_buffer, 2)
        per_person_cost = round(total_budget / max(1, travellers), 2)

        # Category Breakdown
        categories = {
            "Flights": {
                "amount": flights_cost,
                "percentage": round((flights_cost / total_budget) * 100, 1),
                "notes": f"Estimated roundtrip for {travellers} traveller(s)"
            },
            "Accommodation": {
                "amount": accommodation_cost,
                "percentage": round((accommodation_cost / total_budget) * 100, 1),
                "notes": f"{nights} nights across {rooms_needed} room(s)"
            },
            "Food & Dining": {
                "amount": food_cost,
                "percentage": round((food_cost / total_budget) * 100, 1),
                "notes": f"Daily meals, snacks, and specialty dining for {duration_days} days"
            },
            "Local Transportation": {
                "amount": local_transport_cost,
                "percentage": round((local_transport_cost / total_budget) * 100, 1),
                "notes": "City subway passes, regional train transfers, and short taxis"
            },
            "Activities & Entry Fees": {
                "amount": activities_cost,
                "percentage": round((activities_cost / total_budget) * 100, 1),
                "notes": "Curated cultural workshops, landmark admissions, and tours"
            },
            "Miscellaneous & Shopping": {
                "amount": misc_cost,
                "percentage": round((misc_cost / total_budget) * 100, 1),
                "notes": "eSIM mobile connectivity, personal sundries, and local souvenirs"
            },
            "Emergency Buffer": {
                "amount": emergency_buffer,
                "percentage": round((emergency_buffer / total_budget) * 100, 1),
                "notes": "7% contingency reserve for medical, route changes, or unforeseen expenses"
            }
        }

        # Budget Advice
        advice_parts = [
            f"Total estimated trip expenditure is {currency} {total_budget:,.2f} ({currency} {per_person_cost:,.2f} per person)."
        ]
        if target_budget:
            diff = target_budget - total_budget
            if diff >= 0:
                advice_parts.append(f"Estimated costs are well within your target budget of {currency} {target_budget:,.2f} with a surplus buffer of {currency} {diff:,.2f}.")
            else:
                advice_parts.append(f"Estimated costs exceed your target budget of {currency} {target_budget:,.2f} by {currency} {abs(diff):,.2f}. Consider booking accommodations earlier or choosing budget airline connections to optimize.")

        advice_parts.append("Note: All figures are realistic estimates and subject to seasonal flight fluctuations and booking dates.")

        return {
            "flights_cost": flights_cost,
            "accommodation_cost": accommodation_cost,
            "food_cost": food_cost,
            "local_transport_cost": local_transport_cost,
            "activities_cost": activities_cost,
            "misc_cost": misc_cost,
            "emergency_buffer": emergency_buffer,
            "subtotal": subtotal,
            "total_budget": total_budget,
            "per_person_cost": per_person_cost,
            "currency": currency,
            "is_estimate": True,
            "category_breakdown": categories,
            "budget_advice": " ".join(advice_parts)
        }
