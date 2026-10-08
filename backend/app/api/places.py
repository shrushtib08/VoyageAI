import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.geonames import search_places

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/places", tags=["Places"])


@router.get("/search")
def find_places(
    q: str = Query(min_length=2, max_length=100, description="Place name or ASCII-name prefix"),
    country_code: str | None = Query(default=None, min_length=2, max_length=2),
    limit: int = Query(default=10, ge=1, le=25),
    db: Session = Depends(get_db),
):
    q = q.strip()
    if len(q) < 2:
        raise HTTPException(status_code=422, detail="q must contain at least two non-space characters.")
    if country_code and not re.fullmatch(r"[A-Za-z]{2}", country_code):
        raise HTTPException(status_code=422, detail="country_code must be a two-letter code.")
    try:
        results = search_places(db, q, country_code, limit)
    except SQLAlchemyError as exc:
        logger.exception("GeoNames lookup failed; geographic_places may not be imported.")
        raise HTTPException(
            status_code=503,
            detail="Place lookup is unavailable. Import the GeoNames place data and try again.",
        ) from exc
    return {"results": results, "count": len(results), "source": "GeoNames"}
