import re
import json
import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class TravelManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TravelManagerAgent",
            role="Central Coordinator & Requirements Extractor",
            description="Extracts structured trip parameters, resolves multi-city routes, identifies constraints, and orchestrates specialized research agents."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raw_prompt = context.get("raw_prompt", "")
        structured_input = context.get("structured_input", {})

        if raw_prompt and not structured_input:
            extracted = await self.parse_natural_language_prompt(raw_prompt)
        elif structured_input:
            extracted = structured_input.copy()
            if raw_prompt:
                extracted["raw_prompt"] = raw_prompt
            # Ensure defaults
            extracted.setdefault("duration_days", 7)
            extracted.setdefault("travellers", 1)
            extracted.setdefault("currency", "INR")
            extracted.setdefault("travel_style", "balanced")
            extracted.setdefault("interests", ["culture", "sightseeing"])
            extracted.setdefault("dietary_preferences", [])
            extracted.setdefault("constraints", [])
        else:
            raise ValueError("Neither raw_prompt nor structured_input was provided to TravelManagerAgent.")

        # Multi-city detection if destination contains commas, 'and', etc.
        dest = extracted.get("destination", "Tokyo")
        multi_cities = self.detect_multi_cities(dest)
        extracted["multi_cities"] = multi_cities

        return extracted

    async def parse_natural_language_prompt(self, prompt: str) -> Dict[str, Any]:
        """Uses LLM to extract structured travel parameters from freeform text with robust heuristic fallback."""
        system_prompt = (
            "You are the Travel Manager Agent for VoyageAI. Extract structured travel requirements from the user's prompt. "
            "Return JSON with the following keys:\n"
            "- origin: string or null\n"
            "- destination: string (e.g. 'Japan' or 'Paris, Rome and Florence')\n"
            "- duration_days: integer (default 7)\n"
            "- travellers: integer (default 1 or 2 if 'for two' / 'couple')\n"
            "- budget: float or null (extract number, e.g. 150000 for ₹1,50,000 or 1.5 lakh)\n"
            "- currency: string (e.g. 'INR', 'USD', 'EUR', 'GBP')\n"
            "- travel_style: string ('budget', 'luxury', 'balanced', 'adventure', 'relaxed')\n"
            "- interests: array of strings (e.g. ['food', 'culture', 'photography', 'nature'])\n"
            "- dietary_preferences: array of strings (e.g. ['vegetarian'])\n"
            "- accommodation_preferences: string (e.g. 'boutique', '3-4 star', 'hostel', 'luxury')\n"
            "- constraints: array of strings (e.g. ['keep under ₹1.5 lakh', 'relaxed pace'])\n"
            "- travel_month_or_dates: string or null (e.g. 'December')\n"
            "- trip_title: string (e.g. '7-Day Cultural Journey to Japan')\n"
        )

        user_content = f"User trip prompt: \"{prompt}\""

        if llm_service.is_available():
            try:
                data = await llm_service.generate_json(user_content, system_prompt=system_prompt)
                return self.sanitize_extracted_data(data, prompt)
            except Exception as e:
                logger.warning(f"LLM extraction failed, using fallback heuristic parser: {e}")

        # Heuristic fallback parser
        return self.fallback_heuristic_parser(prompt)

    def detect_multi_cities(self, destination: str) -> List[str]:
        cleaned = destination.replace(" and ", ", ").replace("&", ",")
        cities = [c.strip() for c in cleaned.split(",") if c.strip()]
        return cities if len(cities) > 1 else [destination]

    def sanitize_extracted_data(self, data: Dict[str, Any], raw_prompt: str) -> Dict[str, Any]:
        duration = data.get("duration_days") or 7
        try:
            duration = int(duration)
        except Exception:
            duration = 7

        travellers = data.get("travellers") or 1
        try:
            travellers = int(travellers)
        except Exception:
            travellers = 1

        budget = data.get("budget")
        if budget is not None:
            try:
                budget = float(budget)
            except Exception:
                budget = None

        currency = data.get("currency") or "INR"
        destination = data.get("destination") or "Unknown Destination"
        origin = data.get("origin")
        travel_style = data.get("travel_style") or "balanced"
        interests = data.get("interests") or ["sightseeing", "culture"]
        dietary = data.get("dietary_preferences") or []
        accommodation = data.get("accommodation_preferences") or "Boutique / 3-4 star"
        constraints = data.get("constraints") or []
        title = data.get("trip_title") or f"{duration}-Day Trip to {destination}"

        return {
            "origin": origin,
            "destination": destination,
            "duration_days": duration,
            "travellers": travellers,
            "budget": budget,
            "currency": currency,
            "travel_style": travel_style,
            "interests": interests,
            "dietary_preferences": dietary,
            "accommodation_preferences": accommodation,
            "constraints": constraints,
            "start_date": data.get("travel_month_or_dates") or "Upcoming",
            "end_date": None,
            "trip_title": title,
            "raw_prompt": raw_prompt,
        }

    def fallback_heuristic_parser(self, prompt: str) -> Dict[str, Any]:
        """Intelligent regex-based parser when LLM is unavailable."""
        lower = prompt.lower()

        # Extract days
        days = 7
        match_days = re.search(r"(\d+)\s*[- ]*(day|days|night|nights)", lower)
        if match_days:
            days = int(match_days.group(1))

        # Extract travellers
        travellers = 1
        if "two" in lower or "2 people" in lower or "couple" in lower:
            travellers = 2
        elif "family" in lower or "4 people" in lower or "four" in lower:
            travellers = 4
        elif "3 people" in lower or "three" in lower:
            travellers = 3
        else:
            match_ppl = re.search(r"(\d+)\s*(people|person|traveler|traveller|pax)", lower)
            if match_ppl:
                travellers = int(match_ppl.group(1))

        # Extract budget
        budget = None
        currency = "INR" if ("₹" in prompt or "inr" in lower or "rupee" in lower or "lakh" in lower) else "USD"
        match_lakh = re.search(r"(\d+(\.\d+)?)\s*(lakh|lac)", lower)
        if match_lakh:
            budget = float(match_lakh.group(1)) * 100000
            currency = "INR"
        else:
            # Match currency symbols followed by numbers with optional commas (supporting both 1,50,000 and 150,000)
            match_num = re.search(r"(?:₹|\$|€|£|rs\.?|inr|usd|budget\s+is\s+)?([0-9]+(?:,[0-9]+)+|[0-9]{4,})", lower)
            if match_num:
                raw_num = match_num.group(1).replace(",", "")
                budget = float(raw_num)

        # Extract origin & destination
        origin = None
        destination = "Japan"
        match_route = re.search(r"(?:to|visit|visiting)\s+([A-Za-z\s,]+?)\s+(?:from)\s+([A-Za-z\s]+)", prompt, re.IGNORECASE)
        if match_route:
            destination = match_route.group(1).strip()
            origin = match_route.group(2).strip().split()[0]
        else:
            match_from = re.search(r"(?:from)\s+([A-Za-z]+)", prompt, re.IGNORECASE)
            if match_from:
                origin = match_from.group(1).strip()
            match_to = re.search(r"(?:to|in)\s+([A-Za-z\s,]+?)(?:\s+from|\s+for|\s+with|\s+in\s+december|\.|$)", prompt, re.IGNORECASE)
            if match_to:
                destination = match_to.group(1).strip()

        # Interests
        known_interests = ["food", "culture", "photography", "nature", "adventure", "shopping", "nightlife", "history", "relaxation", "art"]
        found_interests = [i for i in known_interests if i in lower]
        if not found_interests:
            found_interests = ["culture", "food", "sightseeing"]

        # Dietary
        dietary = []
        if "vegetarian" in lower or "veg" in lower:
            dietary.append("vegetarian")
        if "vegan" in lower:
            dietary.append("vegan")
        if "halal" in lower:
            dietary.append("halal")

        # Constraints
        constraints = []
        if budget:
            constraints.append(f"Budget capped around {currency} {budget:,.0f}")
        if "relaxed" in lower:
            constraints.append("Pacing must be relaxed with ample free time")
        if "no luxury" in lower:
            constraints.append("Avoid luxury accommodations")

        return {
            "origin": origin or "Bangalore",
            "destination": destination,
            "duration_days": days,
            "travellers": travellers,
            "budget": budget or 150000.0,
            "currency": currency,
            "travel_style": "relaxed" if "relaxed" in lower else "balanced",
            "interests": found_interests,
            "dietary_preferences": dietary,
            "accommodation_preferences": "Boutique / 3-4 star",
            "constraints": constraints,
            "start_date": "December" if "december" in lower else "Upcoming",
            "end_date": None,
            "trip_title": f"{days}-Day Journey to {destination}",
            "raw_prompt": prompt,
        }
