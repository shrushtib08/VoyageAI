from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session


PLACE_COLUMNS = """
    geoname_id, name, ascii_name, latitude, longitude,
    feature_code, country_code, admin1_code, population, timezone
"""


def search_places(
    db: Session,
    query: str,
    country_code: str | None = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    escaped_query = query.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_")
    params = {
        "query": query.strip().lower(),
        "prefix": f"{escaped_query}%",
        "country_code": country_code.upper() if country_code else None,
        "limit": limit,
    }
    rows = db.execute(
        text(
            f"""
            SELECT {PLACE_COLUMNS}
            FROM geographic_places
            WHERE feature_class = 'P'
              AND population > 0
              AND (:country_code IS NULL OR country_code = :country_code)
              AND (
                  LOWER(name) LIKE LOWER(:prefix) ESCAPE '!'
                  OR LOWER(ascii_name) LIKE LOWER(:prefix) ESCAPE '!'
              )
            ORDER BY
                CASE
                    WHEN LOWER(name) = :query THEN 0
                    WHEN LOWER(ascii_name) = :query THEN 1
                    ELSE 2
                END,
                population DESC,
                name
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]


def render_country_reference(country_code: str, places: List[Dict[str, Any]]) -> str:
    code = country_code.upper()
    lines = [
        f"# GeoNames populated places reference: {code}",
        "",
        "This document is a geographic lookup reference, not travel advice. "
        "Population figures and administrative labels come from the source dataset "
        "and may be out of date.",
        "",
        f"Country code: {code}",
        "",
        "## Populated places",
        "",
    ]
    for place in places:
        details = [f"country {place['country_code']}"]
        if place.get("admin1_code"):
            details.append(f"admin1 {place['admin1_code']}")
        if place.get("population") is not None:
            details.append(f"population {place['population']:,}")
        if place.get("timezone"):
            details.append(f"time zone {place['timezone']}")
        if place.get("latitude") is not None and place.get("longitude") is not None:
            details.append(f"coordinates {place['latitude']}, {place['longitude']}")
        lines.append(f"- **{place['name']}** ({'; '.join(details)})")
        ascii_name = place.get("ascii_name")
        if ascii_name and ascii_name.casefold() != place["name"].casefold():
            lines.append(f"  - ASCII name: {ascii_name}")

    lines.extend(
        [
            "",
            "Source: GeoNames (https://www.geonames.org/), licensed under CC BY 4.0.",
            "Verify current population, boundaries, and local travel information independently.",
            "",
        ]
    )
    return "\n".join(lines)


def get_country_places(db: Session, country_code: str, limit: int = 100) -> List[Dict[str, Any]]:
    rows = db.execute(
        text(
            f"""
            SELECT {PLACE_COLUMNS}
            FROM geographic_places
            WHERE country_code = :country_code
              AND feature_class = 'P'
              AND population > 0
            ORDER BY population DESC, name
            LIMIT :limit
            """
        ),
        {"country_code": country_code.upper(), "limit": limit},
    ).mappings().all()
    return [dict(row) for row in rows]
