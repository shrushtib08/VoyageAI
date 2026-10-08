from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.places import router
from app.database.session import get_db
from app.services.geonames import get_country_places, render_country_reference, search_places


def make_places_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE geographic_places (
                    geoname_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ascii_name TEXT,
                    latitude FLOAT,
                    longitude FLOAT,
                    feature_code TEXT,
                    country_code TEXT,
                    admin1_code TEXT,
                    population INTEGER,
                    timezone TEXT,
                    feature_class TEXT
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO geographic_places
                    (geoname_id, name, ascii_name, latitude, longitude, feature_code,
                     country_code, admin1_code, population, timezone, feature_class)
                VALUES
                    (1, 'Tokyo', 'Tokyo', 35.68, 139.69, 'PPLC', 'JP', '40', 13960000, 'Asia/Tokyo', 'P'),
                    (2, 'Tokushima', 'Tokushima', 34.07, 134.56, 'PPLA', 'JP', '36', 250000, 'Asia/Tokyo', 'P'),
                    (3, 'Tokyo Bay', 'Tokyo Bay', 35.5, 139.8, 'BAY', 'JP', NULL, 0, 'Asia/Tokyo', 'H'),
                    (4, 'Tokyo Annex', 'Tokyo Annex', 35.0, 139.0, 'PPL', 'US', 'CA', 1000, 'America/Los_Angeles', 'P'),
                    (5, '100% Town', '100% Town', 20.0, 20.0, 'PPL', 'JP', '01', 5, 'Asia/Tokyo', 'P'),
                    (6, '100x Town', '100x Town', 21.0, 21.0, 'PPL', 'JP', '01', 5, 'Asia/Tokyo', 'P')
                """
            )
        )
    return engine


def test_search_returns_populated_places_and_filters_country_and_literal_prefix():
    engine = make_places_db()
    try:
        with Session(engine) as db:
            results = search_places(db, "tok", country_code="jp")
            assert [place["name"] for place in results] == ["Tokyo", "Tokushima"]

            literal_percent = search_places(db, "100%", country_code="JP")
            assert [place["name"] for place in literal_percent] == ["100% Town"]
    finally:
        engine.dispose()


def test_country_export_is_limited_and_contains_geo_names_attribution():
    engine = make_places_db()
    try:
        with Session(engine) as db:
            places = get_country_places(db, "jp", limit=1)
        markdown = render_country_reference("jp", places)

        assert len(places) == 1
        assert "**Tokyo**" in markdown
        assert "CC BY 4.0" in markdown
        assert "not travel advice" in markdown
    finally:
        engine.dispose()


def test_place_search_api_returns_matching_records_and_validates_input():
    engine = make_places_db()
    app = FastAPI()
    app.include_router(router, prefix="/api")

    def override_get_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/places/search",
                params={"q": "tokyo", "country_code": "JP"},
            )
            assert response.status_code == 200
            assert response.json()["count"] == 1
            assert response.json()["results"][0]["name"] == "Tokyo"
            assert response.json()["source"] == "GeoNames"

            invalid = client.get("/api/places/search", params={"q": "x"})
            assert invalid.status_code == 422
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
