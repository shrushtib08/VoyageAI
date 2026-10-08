import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session

from app.models.trip import Trip, TripRequest, AgentRun, TripStatus, AgentRunStatus
from app.models.research import (
    FlightResearch,
    HotelResearch,
    DestinationResearch,
    WeatherResearch,
    FoodResearch,
    ActivityResearch,
    ResearchSource,
)
from app.models.budget import Budget
from app.models.itinerary import Itinerary, ItineraryDay
from app.models.chat import Conversation, Message

from app.agents.manager import TravelManagerAgent
from app.agents.flight import FlightAgent
from app.agents.hotel import HotelAgent
from app.agents.destination import DestinationResearchAgent
from app.agents.weather import WeatherAgent
from app.agents.food import FoodAgent
from app.agents.activity import ActivityAgent
from app.agents.budget import BudgetAgent
from app.agents.itinerary import ItineraryAgent
from app.agents.critic import CriticAgent

logger = logging.getLogger(__name__)


# Global progress tracker for live UI polling & SSE streaming
_active_progress_stores: Dict[int, Dict[str, Any]] = {}


class MultiAgentOrchestrator:
    def __init__(self):
        self.manager_agent = TravelManagerAgent()
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.destination_agent = DestinationResearchAgent()
        self.weather_agent = WeatherAgent()
        self.food_agent = FoodAgent()
        self.activity_agent = ActivityAgent()
        self.budget_agent = BudgetAgent()
        self.itinerary_agent = ItineraryAgent()
        self.critic_agent = CriticAgent()

    @staticmethod
    def get_progress(trip_id: int) -> Optional[Dict[str, Any]]:
        return _active_progress_stores.get(trip_id)

    def _update_progress(
        self,
        trip_id: int,
        agent_name: str,
        status: str,
        message: str,
        progress_pct: int,
        db: Optional[Session] = None
    ):
        if trip_id not in _active_progress_stores:
            _active_progress_stores[trip_id] = {
                "trip_id": trip_id,
                "current_stage": agent_name,
                "progress_percentage": progress_pct,
                "status": "running",
                "message": message,
                "agents": {
                    "TravelManagerAgent": {"status": "pending", "message": "Awaiting coordinator"},
                    "FlightAgent": {"status": "pending", "message": "Queued"},
                    "HotelAgent": {"status": "pending", "message": "Queued"},
                    "DestinationAgent": {"status": "pending", "message": "Queued"},
                    "WeatherAgent": {"status": "pending", "message": "Queued"},
                    "FoodAgent": {"status": "pending", "message": "Queued"},
                    "ActivityAgent": {"status": "pending", "message": "Queued"},
                    "BudgetAgent": {"status": "pending", "message": "Queued"},
                    "ItineraryAgent": {"status": "pending", "message": "Queued"},
                    "CriticAgent": {"status": "pending", "message": "Queued"},
                },
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

        store = _active_progress_stores[trip_id]
        store["current_stage"] = agent_name
        store["progress_percentage"] = progress_pct
        store["message"] = message
        store["updated_at"] = datetime.now(timezone.utc).isoformat()
        if agent_name in store["agents"]:
            store["agents"][agent_name]["status"] = status
            store["agents"][agent_name]["message"] = message

        # Update DB AgentRun record if db provided
        if db:
            try:
                run = db.query(AgentRun).filter(
                    AgentRun.trip_id == trip_id,
                    AgentRun.agent_name == agent_name
                ).first()
                if not run:
                    run = AgentRun(
                        trip_id=trip_id,
                        agent_name=agent_name,
                        status=AgentRunStatus(status),
                        started_at=datetime.now(timezone.utc),
                        logs=message
                    )
                    db.add(run)
                else:
                    run.status = AgentRunStatus(status)
                    run.logs = f"{run.logs or ''}\n{message}".strip()
                    if status in ["completed", "failed"]:
                        run.completed_at = datetime.now(timezone.utc)
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to record AgentRun in DB: {e}")
                db.rollback()

    async def plan_trip(
        self,
        trip_id: int,
        raw_prompt: str,
        structured_input: Optional[Dict[str, Any]],
        db: Session
    ) -> Trip:
        """Full end-to-end multi-agent orchestration execution."""
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip with id {trip_id} not found.")

        trip.status = TripStatus.PLANNING
        db.commit()

        context: Dict[str, Any] = {
            "trip_id": trip_id,
            "raw_prompt": raw_prompt,
            "structured_input": structured_input or {},
        }

        try:
            # ---------------------------------------------------------
            # 1. Travel Manager Agent
            # ---------------------------------------------------------
            self._update_progress(trip_id, "TravelManagerAgent", "running", "Analyzing requirements and structuring trip parameters...", 10, db)
            manager_res = await self.manager_agent.execute(context)
            if manager_res["status"] == "failed":
                raise RuntimeError(f"TravelManagerAgent failed: {manager_res['error']}")

            manager_data = manager_res["data"]
            context.update(manager_data)
            self._update_progress(trip_id, "TravelManagerAgent", "completed", "Trip parameters structured successfully.", 20, db)

            # Update Trip Entity with extracted details
            trip.title = manager_data.get("trip_title", f"Trip to {manager_data.get('destination')}")
            trip.origin = manager_data.get("origin")
            trip.destination = manager_data.get("destination")
            trip.start_date = manager_data.get("start_date")
            trip.duration_days = manager_data.get("duration_days", 7)
            trip.travellers = manager_data.get("travellers", 1)
            trip.budget = manager_data.get("budget")
            trip.currency = manager_data.get("currency", "INR")
            trip.travel_style = manager_data.get("travel_style", "balanced")
            trip.interests = manager_data.get("interests", [])
            trip.dietary_preferences = manager_data.get("dietary_preferences", [])
            trip.accommodation_preferences = manager_data.get("accommodation_preferences")
            db.commit()

            # Record or update TripRequest
            req_record = db.query(TripRequest).filter(TripRequest.trip_id == trip_id).first()
            if not req_record:
                req_record = TripRequest(
                    trip_id=trip_id,
                    raw_prompt=raw_prompt or str(structured_input),
                    structured_params=manager_data,
                    extracted_constraints={"constraints": manager_data.get("constraints", [])}
                )
                db.add(req_record)
            else:
                req_record.structured_params = manager_data
            db.commit()

            # ---------------------------------------------------------
            # 2. Parallel Specialized Research Agents
            # ---------------------------------------------------------
            self._update_progress(trip_id, "FlightAgent", "running", "Researching airline routes and flight corridors...", 25, db)
            self._update_progress(trip_id, "HotelAgent", "running", "Investigating accommodations in prime districts...", 25, db)
            self._update_progress(trip_id, "DestinationAgent", "running", "Mapping landmarks, cultural heritage, and districts...", 25, db)
            self._update_progress(trip_id, "WeatherAgent", "running", "Retrieving meteorological and seasonal conditions...", 25, db)
            self._update_progress(trip_id, "FoodAgent", "running", "Exploring local delicacies and dining recommendations...", 25, db)
            self._update_progress(trip_id, "ActivityAgent", "running", "Curating and ranking immersive traveler activities...", 25, db)

            parallel_tasks = [
                self.flight_agent.execute(context),
                self.hotel_agent.execute(context),
                self.destination_agent.execute(context),
                self.weather_agent.execute(context),
                self.food_agent.execute(context),
                self.activity_agent.execute(context),
            ]

            results = await asyncio.gather(*parallel_tasks, return_exceptions=True)

            flight_res, hotel_res, dest_res, weather_res, food_res, activity_res = results

            # Process Flight Results
            if isinstance(flight_res, dict) and flight_res.get("status") == "completed":
                context["flight_research"] = flight_res["data"]
                self._update_progress(trip_id, "FlightAgent", "completed", "Flight options researched.", 50, db)
            else:
                context["flight_research"] = {}
                self._update_progress(trip_id, "FlightAgent", "failed", "Flight research incomplete, applying default route.", 50, db)

            # Process Hotel Results
            if isinstance(hotel_res, dict) and hotel_res.get("status") == "completed":
                context["hotel_research"] = hotel_res["data"]
                self._update_progress(trip_id, "HotelAgent", "completed", "Accommodations discovered.", 55, db)
            else:
                context["hotel_research"] = {}
                self._update_progress(trip_id, "HotelAgent", "failed", "Hotel research fallback used.", 55, db)

            # Process Destination Results
            if isinstance(dest_res, dict) and dest_res.get("status") == "completed":
                context["destination_research"] = dest_res["data"]
                self._update_progress(trip_id, "DestinationAgent", "completed", "Attractions and cultural sites cataloged.", 60, db)
            else:
                context["destination_research"] = {}
                self._update_progress(trip_id, "DestinationAgent", "failed", "Destination research fallback used.", 60, db)

            # Process Weather Results
            if isinstance(weather_res, dict) and weather_res.get("status") == "completed":
                context["weather_research"] = weather_res["data"]
                self._update_progress(trip_id, "WeatherAgent", "completed", "Climate & weather conditions analyzed.", 65, db)
            else:
                context["weather_research"] = {}
                self._update_progress(trip_id, "WeatherAgent", "failed", "Weather analysis fallback used.", 65, db)

            # Process Food Results
            if isinstance(food_res, dict) and food_res.get("status") == "completed":
                context["food_research"] = food_res["data"]
                self._update_progress(trip_id, "FoodAgent", "completed", "Culinary guide and dining recommendations ready.", 70, db)
            else:
                context["food_research"] = {}
                self._update_progress(trip_id, "FoodAgent", "failed", "Food research fallback used.", 70, db)

            # Process Activity Results
            if isinstance(activity_res, dict) and activity_res.get("status") == "completed":
                context["activity_research"] = activity_res["data"]
                self._update_progress(trip_id, "ActivityAgent", "completed", "Experiential activities ranked.", 75, db)
            else:
                context["activity_research"] = {}
                self._update_progress(trip_id, "ActivityAgent", "failed", "Activity research fallback used.", 75, db)

            # ---------------------------------------------------------
            # 3. Budget Agent
            # ---------------------------------------------------------
            self._update_progress(trip_id, "BudgetAgent", "running", "Aggregating category costs and financial allocations...", 80, db)
            budget_res = await self.budget_agent.execute(context)
            if budget_res.get("status") == "completed":
                context["budget_details"] = budget_res["data"]
                self._update_progress(trip_id, "BudgetAgent", "completed", "Comprehensive budget calculated.", 85, db)
            else:
                context["budget_details"] = {}
                self._update_progress(trip_id, "BudgetAgent", "failed", "Budget estimation fallback applied.", 85, db)

            # ---------------------------------------------------------
            # 4. Itinerary Agent & Critic Agent Loop
            # ---------------------------------------------------------
            self._update_progress(trip_id, "ItineraryAgent", "running", "Assembling day-by-day scheduled timeline...", 88, db)
            revision_count = 0
            critic_feedback = None

            while True:
                context["revision_count"] = revision_count
                context["critic_feedback"] = critic_feedback

                itin_res = await self.itinerary_agent.execute(context)
                itinerary_data = itin_res.get("data") or {}
                context["itinerary"] = itinerary_data

                # Critic Agent checks
                self._update_progress(trip_id, "CriticAgent", "running", f"Auditing itinerary feasibility (Round {revision_count + 1})...", 92, db)
                critic_res = await self.critic_agent.execute(context)
                critic_data = critic_res.get("data") or {}

                validation_status = critic_data.get("status", "VALID")
                if validation_status == "VALID" or revision_count >= 1:
                    itinerary_data["validation_status"] = "VALID"
                    itinerary_data["critique_notes"] = critic_data.get("critique_notes", "Itinerary validated.")
                    itinerary_data["validation_flags"] = critic_data.get("issues_found", [])
                    itinerary_data["revision_count"] = revision_count
                    self._update_progress(trip_id, "ItineraryAgent", "completed", "Itinerary optimized and finalized.", 96, db)
                    self._update_progress(trip_id, "CriticAgent", "completed", "Itinerary audited and verified as feasible.", 98, db)
                    break
                else:
                    # Request revision from Itinerary Agent
                    revision_count += 1
                    critic_feedback = "\n".join(critic_data.get("revision_suggestions", []))
                    self._update_progress(trip_id, "CriticAgent", "running", "Critic flagged adjustments; refining schedule...", 90, db)
                    self._update_progress(trip_id, "ItineraryAgent", "running", "Refining schedule based on critique...", 91, db)

            # ---------------------------------------------------------
            # 5. Save all entities to Database
            # ---------------------------------------------------------
            self._persist_research_and_itinerary(trip, context, db)

            trip.status = TripStatus.COMPLETED
            trip.summary = itinerary_data.get("overview", f"Custom multi-agent travel plan for {trip.destination}")
            db.commit()

            # Finalize progress store
            if trip_id in _active_progress_stores:
                _active_progress_stores[trip_id]["status"] = "completed"
                _active_progress_stores[trip_id]["progress_percentage"] = 100
                _active_progress_stores[trip_id]["message"] = "Your complete travel plan is ready!"

            logger.info(f"Trip {trip_id} multi-agent orchestration completed successfully.")
            return trip

        except Exception as e:
            logger.error(f"Trip {trip_id} orchestration failed: {e}", exc_info=True)
            trip.status = TripStatus.FAILED
            db.commit()
            if trip_id in _active_progress_stores:
                _active_progress_stores[trip_id]["status"] = "failed"
                _active_progress_stores[trip_id]["message"] = f"Orchestration error: {str(e)}"
            raise e

    def _persist_research_and_itinerary(self, trip: Trip, context: Dict[str, Any], db: Session):
        """Stores all researched components into the relational schema."""
        trip_id = trip.id

        # 1. Flight Research
        f_data = context.get("flight_research", {})
        if f_data:
            existing_f = db.query(FlightResearch).filter(FlightResearch.trip_id == trip_id).first()
            if not existing_f:
                existing_f = FlightResearch(trip_id=trip_id)
                db.add(existing_f)
            existing_f.origin_airport = f_data.get("origin_airport")
            existing_f.destination_airport = f_data.get("destination_airport")
            existing_f.route_summary = f_data.get("route_summary")
            existing_f.direct_options = f_data.get("direct_options", [])
            existing_f.connecting_options = f_data.get("connecting_options", [])
            existing_f.airlines = f_data.get("airlines", [])
            existing_f.fare_range_low = f_data.get("fare_range_low")
            existing_f.fare_range_high = f_data.get("fare_range_high")
            existing_f.estimated_duration_hours = f_data.get("estimated_duration_hours")
            existing_f.currency = f_data.get("currency", trip.currency)
            existing_f.is_live_data = f_data.get("is_live_data", False)
            existing_f.api_status_note = f_data.get("api_status_note")
            existing_f.source_citations = f_data.get("source_citations", [])

        # 2. Hotel Research
        h_data = context.get("hotel_research", {})
        if h_data:
            existing_h = db.query(HotelResearch).filter(HotelResearch.trip_id == trip_id).first()
            if not existing_h:
                existing_h = HotelResearch(trip_id=trip_id)
                db.add(existing_h)
            existing_h.recommendations = h_data.get("recommendations", [])
            existing_h.budget_category = h_data.get("budget_category")
            existing_h.avg_nightly_price = h_data.get("avg_nightly_price")
            existing_h.currency = h_data.get("currency", trip.currency)
            existing_h.is_live_data = h_data.get("is_live_data", False)
            existing_h.api_status_note = h_data.get("api_status_note")
            existing_h.source_citations = h_data.get("source_citations", [])

        # 3. Destination Research
        d_data = context.get("destination_research", {})
        if d_data:
            existing_d = db.query(DestinationResearch).filter(DestinationResearch.trip_id == trip_id).first()
            if not existing_d:
                existing_d = DestinationResearch(trip_id=trip_id)
                db.add(existing_d)
            existing_d.major_attractions = d_data.get("major_attractions", [])
            existing_d.cultural_sites = d_data.get("cultural_sites", [])
            existing_d.lesser_known_gems = d_data.get("lesser_known_gems", [])
            existing_d.neighborhoods = d_data.get("neighborhoods", [])
            existing_d.local_tips = d_data.get("local_tips", [])
            existing_d.practical_info = d_data.get("practical_info", {})
            existing_d.source_citations = d_data.get("source_citations", [])

        # 4. Weather Research
        w_data = context.get("weather_research", {})
        if w_data:
            existing_w = db.query(WeatherResearch).filter(WeatherResearch.trip_id == trip_id).first()
            if not existing_w:
                existing_w = WeatherResearch(trip_id=trip_id, destination=trip.destination)
                db.add(existing_w)
            existing_w.season_summary = w_data.get("season_summary")
            existing_w.avg_temp_min = w_data.get("avg_temp_min")
            existing_w.avg_temp_max = w_data.get("avg_temp_max")
            existing_w.precipitation_probability = w_data.get("precipitation_probability")
            existing_w.weather_conditions = w_data.get("weather_conditions")
            existing_w.travel_advice = w_data.get("travel_advice")
            existing_w.packing_suggestions = w_data.get("packing_suggestions", [])
            existing_w.is_live_forecast = w_data.get("is_live_forecast", False)
            existing_w.api_status_note = w_data.get("api_status_note")

        # 5. Food Research
        food_data = context.get("food_research", {})
        if food_data:
            existing_food = db.query(FoodResearch).filter(FoodResearch.trip_id == trip_id).first()
            if not existing_food:
                existing_food = FoodResearch(trip_id=trip_id)
                db.add(existing_food)
            existing_food.local_dishes = food_data.get("local_dishes", [])
            existing_food.popular_food_areas = food_data.get("popular_food_areas", [])
            existing_food.recommended_spots = food_data.get("recommended_spots", [])
            existing_food.street_food = food_data.get("street_food", [])
            existing_food.dietary_suitability = food_data.get("dietary_suitability", {})
            existing_food.price_level_summary = food_data.get("price_level_summary")
            existing_food.source_citations = food_data.get("source_citations", [])

        # 6. Activity Research
        act_data = context.get("activity_research", {})
        if act_data:
            existing_act = db.query(ActivityResearch).filter(ActivityResearch.trip_id == trip_id).first()
            if not existing_act:
                existing_act = ActivityResearch(trip_id=trip_id)
                db.add(existing_act)
            existing_act.ranked_activities = act_data.get("ranked_activities", [])
            existing_act.source_citations = act_data.get("source_citations", [])

        # 7. Budget Details
        b_data = context.get("budget_details", {})
        if b_data:
            existing_b = db.query(Budget).filter(Budget.trip_id == trip_id).first()
            if not existing_b:
                existing_b = Budget(trip_id=trip_id)
                db.add(existing_b)
            existing_b.flights_cost = b_data.get("flights_cost", 0.0)
            existing_b.accommodation_cost = b_data.get("accommodation_cost", 0.0)
            existing_b.food_cost = b_data.get("food_cost", 0.0)
            existing_b.local_transport_cost = b_data.get("local_transport_cost", 0.0)
            existing_b.activities_cost = b_data.get("activities_cost", 0.0)
            existing_b.misc_cost = b_data.get("misc_cost", 0.0)
            existing_b.emergency_buffer = b_data.get("emergency_buffer", 0.0)
            existing_b.subtotal = b_data.get("subtotal", 0.0)
            existing_b.total_budget = b_data.get("total_budget", 0.0)
            existing_b.per_person_cost = b_data.get("per_person_cost", 0.0)
            existing_b.currency = b_data.get("currency", trip.currency)
            existing_b.is_estimate = b_data.get("is_estimate", True)
            existing_b.category_breakdown = b_data.get("category_breakdown", {})
            existing_b.budget_advice = b_data.get("budget_advice")

        # 8. Itinerary and Days
        itin_data = context.get("itinerary", {})
        if itin_data:
            existing_itin = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).first()
            if not existing_itin:
                existing_itin = Itinerary(trip_id=trip_id)
                db.add(existing_itin)
                db.flush()
            existing_itin.total_days = itin_data.get("total_days", trip.duration_days)
            existing_itin.title = itin_data.get("title")
            existing_itin.overview = itin_data.get("overview")
            existing_itin.validation_status = itin_data.get("validation_status", "VALID")
            existing_itin.critique_notes = itin_data.get("critique_notes")
            existing_itin.validation_flags = itin_data.get("validation_flags", [])
            existing_itin.revision_count = itin_data.get("revision_count", 0)
            existing_itin.practical_tips = itin_data.get("practical_tips", [])

            # Clear old days and add new
            db.query(ItineraryDay).filter(ItineraryDay.itinerary_id == existing_itin.id).delete()
            for d in itin_data.get("days", []):
                day_obj = ItineraryDay(
                    itinerary_id=existing_itin.id,
                    day_number=d.get("day_number", 1),
                    date_str=d.get("date_str"),
                    theme=d.get("theme", "Exploration"),
                    morning=d.get("morning", {}),
                    afternoon=d.get("afternoon", {}),
                    evening=d.get("evening", {}),
                    attractions=d.get("attractions", []),
                    food_suggestions=d.get("food_suggestions", []),
                    transport_notes=d.get("transport_notes"),
                    estimated_daily_spend=d.get("estimated_daily_spend", 0.0),
                    practical_notes=d.get("practical_notes"),
                )
                db.add(day_obj)

        # 9. Aggregate Sources
        db.query(ResearchSource).filter(ResearchSource.trip_id == trip_id).delete()
        for source_list in [
            f_data.get("source_citations", []),
            h_data.get("source_citations", []),
            d_data.get("source_citations", []),
            food_data.get("source_citations", []),
            act_data.get("source_citations", []),
        ]:
            for s in source_list:
                src_entity = ResearchSource(
                    trip_id=trip_id,
                    agent_name=s.get("agent_name", "ResearchAgent"),
                    title=s.get("title", "Resource"),
                    source_type=s.get("source_type"),
                    url=s.get("url"),
                    snippet=s.get("snippet"),
                )
                db.add(src_entity)

        # 10. Conversation Init
        existing_conv = db.query(Conversation).filter(Conversation.trip_id == trip_id).first()
        if not existing_conv:
            conv = Conversation(trip_id=trip_id)
            db.add(conv)
            db.flush()
            welcome_msg = Message(
                conversation_id=conv.id,
                sender="assistant",
                content=f"Hello! I'm your VoyageAI Travel Concierge. I have coordinated your team of 7 specialized research agents to build your {trip.duration_days}-day itinerary to {trip.destination}. How can I help refine or adapt your plan today?"
            )
            db.add(welcome_msg)

        db.commit()


orchestrator = MultiAgentOrchestrator()
