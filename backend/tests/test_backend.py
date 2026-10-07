import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db
from app.agents.manager import TravelManagerAgent
from app.agents.budget import BudgetAgent
from app.agents.critic import CriticAgent
from app.core.security import hash_password, verify_password

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_voyageai.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_password_hashing():
    pwd = "secretpassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_user_registration_and_login():
    reg_payload = {
        "email": "traveler@voyageai.com",
        "username": "traveler1",
        "password": "mypassword123",
        "full_name": "Voyage Adventurer"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "traveler1"

    # Login
    login_payload = {
        "username_or_email": "traveler1",
        "password": "mypassword123"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()


@pytest.mark.asyncio
async def test_travel_manager_heuristic_extraction():
    agent = TravelManagerAgent()
    prompt = "Plan a 7-day trip to Japan from Bangalore for two people in December. My budget is ₹1,50,000. I like food, culture, photography and nature."
    context = {"raw_prompt": prompt}
    res = await agent.run(context)

    assert res["destination"] == "Japan"
    assert res["origin"] == "Bangalore"
    assert res["duration_days"] == 7
    assert res["travellers"] == 2
    assert res["budget"] == 150000.0
    assert "food" in res["interests"]
    assert "culture" in res["interests"]
    assert "photography" in res["interests"]


@pytest.mark.asyncio
async def test_budget_agent_calculation():
    agent = BudgetAgent()
    context = {
        "budget": 150000.0,
        "currency": "INR",
        "travellers": 2,
        "duration_days": 7,
        "flight_research": {"fare_range_low": 35000.0, "fare_range_high": 45000.0},
        "hotel_research": {"avg_nightly_price": 6000.0},
        "activity_research": {"ranked_activities": [{"estimated_cost": 2000.0}, {"estimated_cost": 1500.0}]}
    }
    res = await agent.run(context)
    assert res["flights_cost"] > 0
    assert res["accommodation_cost"] > 0
    assert res["emergency_buffer"] > 0
    assert res["total_budget"] > 0
    assert res["per_person_cost"] == round(res["total_budget"] / 2, 2)
    assert "Flights" in res["category_breakdown"]


@pytest.mark.asyncio
async def test_critic_agent_validation():
    critic = CriticAgent()
    context = {
        "itinerary": {
            "total_days": 3,
            "days": [
                {
                    "day_number": 1,
                    "theme": "Arrival & City Stroll",
                    "attractions": ["Tokyo Tower"],
                    "morning": {"activity": "Arrive and check in"},
                    "afternoon": {"activity": "Visit tower"},
                    "evening": {"activity": "Dinner in Ginza"}
                },
                {
                    "day_number": 2,
                    "theme": "Historic Shrines",
                    "attractions": ["Senso-ji Temple"],
                    "morning": {"activity": "Explore shrine"},
                    "afternoon": {"activity": "Artisan shops"},
                    "evening": {"activity": "Riverside walk"}
                }
            ]
        },
        "budget_details": {"total_budget": 50000.0},
        "constraints": [],
        "interests": ["culture"],
        "weather_research": {"weather_conditions": "Clear"},
        "revision_count": 0
    }
    audit = await critic.run(context)
    assert audit["status"] in ["VALID", "NEEDS_REVISION"]
    assert "score" in audit


@pytest.mark.asyncio
async def test_end_to_end_orchestration_and_export():
    from app.agents.orchestrator import orchestrator
    from app.models.trip import Trip, TripStatus

    db = TestingSessionLocal()
    try:
        # Create user
        from app.models.user import User
        test_user = User(
            email="e2e_traveler@voyageai.com",
            username="e2e_traveler",
            full_name="E2E Voyager",
            hashed_password=hash_password("testpass123")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Create Trip
        trip = Trip(
            user_id=test_user.id,
            title="Planning Test Trip...",
            destination="Kyoto",
            status=TripStatus.PLANNING
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)

        # Execute orchestrator
        prompt = "Plan a 4-day trip to Kyoto from Tokyo for 2 people with a ₹80,000 budget. I love photography, temples, and ramen."
        completed_trip = await orchestrator.plan_trip(
            trip_id=trip.id,
            raw_prompt=prompt,
            structured_input=None,
            db=db
        )

        assert completed_trip.status == TripStatus.COMPLETED
        assert completed_trip.flight_research is not None
        assert completed_trip.hotel_research is not None
        assert completed_trip.destination_research is not None
        assert completed_trip.weather_research is not None
        assert completed_trip.food_research is not None
        assert completed_trip.activity_research is not None
        assert completed_trip.budget_details is not None
        assert completed_trip.itinerary is not None
        assert len(completed_trip.itinerary.days) == 4
        assert len(completed_trip.sources) > 0
    finally:
        db.close()

