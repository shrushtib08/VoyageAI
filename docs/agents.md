# VoyageAI Specialized Agent Directory

This document details the responsibilities, input contexts, output schemas, and fail-safe logic for all 10 specialized agents within the VoyageAI ecosystem.

---

## 1. Travel Manager Agent (`TravelManagerAgent`)
- **Role**: Central Orchestration & Intent Extraction Coordinator
- **Inputs**: `raw_prompt` (string) or `structured_input` (dictionary).
- **Responsibilities**:
  - Understands freeform travel requests.
  - Extracts 12+ structured criteria: origin, destination(s), multi-city sequences, duration, travelers, budget, currency, style, interests, dietary needs, lodging tier, and explicit constraints.
  - Identifies smart constraints like "no luxury hotels", "max 3h travel", or "strict vegetarian".
- **Fallback**: Regex and heuristic natural-language parser supporting Indian (`1,50,000`) and international currency formats.

---

## 2. Flight Agent (`FlightAgent`)
- **Role**: Flight & Aviation Intelligence Specialist
- **Inputs**: Origin, Destination, Travelers, Currency, Target Budget.
- **Tools**: `AviationService` (AviationStack API).
- **Outputs**: Airport IATA hubs, direct and connecting flight options, scheduled carriers, roundtrip fare range, duration.
- **Live Flag**: Explicitly marks results as `is_live_data = True` only when real-time AviationStack schedules are retrieved. Researched estimates are labeled clearly.

---

## 3. Hotel Agent (`HotelAgent`)
- **Role**: Accommodation & Lodging Specialist
- **Inputs**: Destination, Multi-city sequence, Budget category, Travelers, Duration, Style preferences.
- **Outputs**: Curated list of verified hotels and boutique stays with neighborhood, nightly rates, ratings, amenity chips, and recommendation rationale.
- **Rule**: Never fabricates fictional hotel chains; labels data as researched recommendations.

---

## 4. Destination Research Agent (`DestinationAgent`)
- **Role**: Cultural Heritage & Regional Geography Specialist
- **Inputs**: Destination, Multi-cities, Traveler passions.
- **Tools**: `WebSearchService` (Tavily AI Search).
- **Outputs**: Major monuments, cultural heritage sites, hidden local gems, distinctive neighborhoods, and essential logistics (transit passes, SIM cards, emergency contacts).
- **Citations**: Preserves URL citations and snippets for all external sources.

---

## 5. Weather Agent (`WeatherAgent`)
- **Role**: Meteorological & Seasonal Climate Analyst
- **Inputs**: Destination, Travel timing / season.
- **Tools**: `WeatherService` (OpenWeather API).
- **Outputs**: Min/Max temperatures, rain probability %, conditions summary, weather travel advice, and tailored packing checklists.
- **Rule**: Explains if future travel dates exceed live forecast windows and provides climate guidance.

---

## 6. Food Agent (`FoodAgent`)
- **Role**: Gastronomy & Regional Culinary Specialist
- **Inputs**: Destination, Dietary constraints (veg, vegan, halal, gluten-free), Currency, Budget.
- **Outputs**: Must-try signature dishes, food streets and night markets, recommended dining spots with price tiers, and verified dietary accessibility notes.

---

## 7. Activity Agent (`ActivityAgent`)
- **Role**: Experience & Adventure Curator
- **Inputs**: Destination, Passions, Style, Duration, Currency.
- **Outputs**: Curated activities ranked by relevance (e.g. #1, #2, #3), estimated duration, cost, and optimal time of day (Morning, Sunset Golden Hour, Evening).

---

## 8. Budget Agent (`BudgetAgent`)
- **Role**: Financial & Resource Allocation Strategist
- **Inputs**: Outputs from Flight, Hotel, Food, Transit, and Activity agents.
- **Outputs**:
  - Category breakdown (Flights, Stays, Food, Transit, Activities, Miscellaneous).
  - 7% Emergency Contingency Reserve.
  - Subtotal, Total, and Per-Person rates.
  - Target budget variance analysis.
  - Multi-currency support (INR, USD, EUR, GBP, JPY).

---

## 9. Itinerary Agent (`ItineraryAgent`)
- **Role**: Day-by-Day Scheduling Architect
- **Inputs**: Full aggregated research from prior agents + Critic revision notes if re-executing.
- **Outputs**:
  - Structured daily schedule containing Morning, Afternoon, and Evening blocks.
  - Geographic clustering per day (venues in the same neighborhood to minimize transit fatigue).
  - Daily spending estimates, transit tips, and practical reminders.

---

## 10. Critic / Validation Agent (`CriticAgent`)
- **Role**: Quality Assurance & Feasibility Auditor
- **Inputs**: Generated itinerary, budget allocations, constraints, weather conditions, revision count.
- **Audits**:
  - Unrealistic travel times
  - Geographical backtracking
  - Duplicate attraction visits
  - Budget mismatches
  - Missing rest buffers or meal pauses
- **Outputs**: `VALID` or `NEEDS_REVISION` with quality score (1-100), issues found, and revision suggestions.
- **Guard**: Caps revision cycles at 2 iterations to prevent infinite loops.
