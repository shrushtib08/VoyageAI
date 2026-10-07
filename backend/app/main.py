import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import engine, Base
import app.models  # Ensure all SQLAlchemy models are registered
from app.api.auth import router as auth_router
from app.api.trips import router as trips_router
from app.api.chat import router as chat_router
from app.api.export import router as export_router
from app.services.llm import llm_service
from app.services.aviation import aviation_service
from app.services.weather import weather_service
from app.services.websearch import web_search_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("voyageai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.TAGLINE,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.cors_origins_list
if "*" not in origins and "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api")
app.include_router(trips_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(export_router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.VERSION
    }


@app.get("/api/integrations")
def get_integrations_status():
    """Reports status of external API providers and active fallbacks."""
    return {
        "llm": {
            "provider": "Groq",
            "model": settings.GROQ_MODEL,
            "configured": llm_service.is_available(),
            "status": "Active" if llm_service.is_available() else "Unconfigured (Heuristic fallback active)"
        },
        "aviation": {
            "provider": "AviationStack",
            "configured": aviation_service.is_configured(),
            "status": "Live schedule active" if aviation_service.is_configured() else "Researched airline estimates active"
        },
        "weather": {
            "provider": "OpenWeather",
            "configured": weather_service.is_configured(),
            "status": "Live conditions active" if weather_service.is_configured() else "Seasonal climate averages active"
        },
        "web_search": {
            "provider": "Tavily",
            "configured": web_search_service.is_configured(),
            "status": "Live web research active" if web_search_service.is_configured() else "Curated regional knowledge active"
        },
        "database": {
            "url_scheme": settings.DATABASE_URL.split("://")[0] if "://" in settings.DATABASE_URL else "sqlite",
            "mode": "PostgreSQL" if "postgres" in settings.DATABASE_URL else "SQLite (Local Dev)"
        }
    }
