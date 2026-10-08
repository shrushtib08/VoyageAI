# VoyageAI REST API Documentation

Base URL: `http://localhost:8000/api`

Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Authentication Endpoints

### Register User
- **POST** `/auth/register`
- **Request Body**:
  ```json
  {
    "email": "traveler@voyageai.com",
    "username": "alex-traveler",
    "password": "choose-a-unique-strong-password",
    "full_name": "Alex Traveler"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "traveler@voyageai.com",
      "username": "alex-traveler",
      "full_name": "Alex Traveler",
      "created_at": "2026-10-07T16:00:00Z"
    }
  }
  ```

### Login
- **POST** `/auth/login`
- **Request Body**:
  ```json
  {
    "username_or_email": "alex-traveler",
    "password": "the-password-chosen-during-registration"
  }
  ```
- **Response** (200 OK): JWT token and user profile.

### Current User Profile
- **GET** `/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response** (200 OK): User object.

---

## 2. Trip Orchestration Endpoints

### Plan Trip from Freeform Natural Prompt
- **POST** `/trips/plan-prompt`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "prompt": "Plan a 7-day trip to Japan from Bangalore for two people in December. My budget is ₹1,50,000. I like food, culture, photography and nature."
  }
  ```
- **Response** (201 Created): Trip metadata object with status `planning`. The orchestrator executes asynchronously in the background.

### Plan Trip from Structured Form
- **POST** `/trips/plan-structured`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "origin": "Bangalore",
    "destination": "Japan",
    "duration_days": 7,
    "travellers": 2,
    "budget": 150000.0,
    "currency": "INR",
    "travel_style": "balanced",
    "interests": ["Culture", "Food", "Photography", "Nature"],
    "dietary_preferences": ["Vegetarian"],
    "accommodation_preferences": "Boutique / 3-4 star",
    "special_constraints": "Keep under budget"
  }
  ```

### List User Trips
- **GET** `/trips`
- **Query Params**: `search` (optional string)
- **Response** (200 OK): Array of trip cards.

### Get Complete Trip Dashboard
- **GET** `/trips/{trip_id}`
- **Response** (200 OK): Complete nested object including flight research, hotel recommendations, destination intel, weather norms, gastronomy, ranked activities, budget breakdown, audited itinerary days, and citations.

### Real-Time Live Progress Query
- **GET** `/trips/{trip_id}/progress`
- **Response** (200 OK): Status of all 10 specialized agents and percentage completion.

### Server-Sent Events (SSE) Live Stream
- **GET** `/trips/{trip_id}/stream`
- **Response**: `text/event-stream` stream pushing live updates every 700ms until completion.

### Delete Trip
- **DELETE** `/trips/{trip_id}`
- **Response** (204 No Content).

---

## 3. Trip Memory Follow-Up Chat

### Get Conversation History
- **GET** `/trips/{trip_id}/chat`
- **Response** (200 OK): Conversation object with messages list.

### Post Follow-Up Request
- **POST** `/trips/{trip_id}/chat`
- **Request Body**:
  ```json
  {
    "message": "Make Day 3 more relaxed and add vegetarian restaurants."
  }
  ```
- **Response** (200 OK): Assistant response preserving full itinerary context and returning actions taken.

---

## 4. Export Endpoints

- **GET** `/trips/{trip_id}/export/markdown`: Returns `.md` formatted file download.
- **GET** `/trips/{trip_id}/export/print`: Returns printer-styled HTML page.
- **GET** `/trips/{trip_id}/export/pdf`: Generates and streams PDF document.

---

## 5. System Health & Integration Status

- **GET** `/api/health`: Database and server liveness check.
- **GET** `/api/integrations`: Status of Groq, AviationStack, OpenWeather, Tavily, and PostgreSQL.
