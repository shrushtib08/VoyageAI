import argparse
from pathlib import Path
import re
import sys

from sqlalchemy import inspect

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal  # noqa: E402
from app.services.geonames import get_country_places, render_country_reference  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a small GeoNames populated-place reference for RAG ingestion."
    )
    parser.add_argument("--country", required=True, help="Two-letter ISO country code, e.g. JP")
    parser.add_argument("--output", required=True, type=Path, help="Output Markdown file")
    parser.add_argument("--limit", type=int, default=100, help="Maximum populated places (1-250)")
    args = parser.parse_args()

    country_code = args.country.upper()
    if not re.fullmatch(r"[A-Z]{2}", country_code):
        parser.error("--country must be a two-letter country code.")
    if not 1 <= args.limit <= 250:
        parser.error("--limit must be between 1 and 250.")

    db = SessionLocal()
    try:
        if not inspect(db.get_bind()).has_table("geographic_places"):
            raise RuntimeError(
                "GeoNames place data is unavailable; run import_asia_geonames.py first."
            )
        places = get_country_places(db, country_code, args.limit)
        if not places:
            raise RuntimeError(f"No populated places found for country code {country_code}.")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            render_country_reference(country_code, places),
            encoding="utf-8",
        )
    finally:
        db.close()

    print(f"Wrote {len(places)} place records to {args.output}")


if __name__ == "__main__":
    main()
