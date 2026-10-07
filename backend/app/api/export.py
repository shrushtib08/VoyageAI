import io
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from app.database.session import get_db
from app.models.user import User
from app.models.trip import Trip
from app.api.deps import get_current_user

router = APIRouter(prefix="/trips/{trip_id}/export", tags=["Export"])


def _generate_markdown_doc(trip: Trip) -> str:
    lines = []
    lines.append(f"# {trip.title}")
    lines.append(f"**VoyageAI Multi-Agent Curated Plan**")
    lines.append(f"")
    lines.append(f"- **Destination**: {trip.destination}")
    lines.append(f"- **Origin**: {trip.origin or 'N/A'}")
    lines.append(f"- **Duration**: {trip.duration_days} Days")
    lines.append(f"- **Travelers**: {trip.travellers}")
    lines.append(f"- **Target Budget**: {trip.currency} {trip.budget:,.2f}" if trip.budget else f"- **Target Budget**: Flexible")
    lines.append(f"- **Travel Style**: {trip.travel_style}")
    lines.append(f"- **Interests**: {', '.join(trip.interests) if trip.interests else 'General exploration'}")
    lines.append(f"")
    lines.append(f"## Overview")
    lines.append(f"{trip.summary or 'Custom itinerary designed by VoyageAI multi-agent system.'}")
    lines.append(f"")

    # Flights
    if trip.flight_research:
        f = trip.flight_research
        lines.append(f"## ✈️ Flights & Transit")
        lines.append(f"- **Corridor**: {f.origin_airport} → {f.destination_airport}")
        lines.append(f"- **Estimated Fare**: {f.currency} {f.fare_range_low:,.0f} - {f.fare_range_high:,.0f} (Roundtrip per person)")
        lines.append(f"- **Airlines**: {', '.join(f.airlines)}")
        lines.append(f"- **Data Status**: {'Live Schedule' if f.is_live_data else 'Researched Market Estimate'}")
        lines.append(f"")

    # Hotels
    if trip.hotel_research:
        h = trip.hotel_research
        lines.append(f"## 🏨 Recommended Accommodations")
        for rec in h.recommendations:
            lines.append(f"### {rec.get('name')} ({rec.get('area')})")
            lines.append(f"- **Approx. Rate**: {rec.get('currency', h.currency)} {rec.get('approx_price_per_night', 0):,.0f} / night")
            lines.append(f"- **Rating**: {rec.get('rating', 'N/A')} / 5.0")
            lines.append(f"- **Description**: {rec.get('description')}")
            lines.append(f"- **Why Recommended**: {rec.get('recommendation_reason')}")
            lines.append(f"")

    # Weather
    if trip.weather_research:
        w = trip.weather_research
        lines.append(f"## 🌤️ Weather & Climate")
        lines.append(f"- **Conditions**: {w.weather_conditions}")
        lines.append(f"- **Temperature**: {w.avg_temp_min}°C to {w.avg_temp_max}°C")
        lines.append(f"- **Rain Probability**: {w.precipitation_probability}%")
        lines.append(f"- **Travel Advice**: {w.travel_advice}")
        lines.append(f"- **Packing Tips**: {', '.join(w.packing_suggestions)}")
        lines.append(f"")

    # Budget
    if trip.budget_details:
        b = trip.budget_details
        lines.append(f"## 💰 Estimated Budget Breakdown")
        lines.append(f"| Category | Estimated Cost ({b.currency}) |")
        lines.append(f"|---|---|")
        lines.append(f"| Flights | {b.flights_cost:,.2f} |")
        lines.append(f"| Accommodation | {b.accommodation_cost:,.2f} |")
        lines.append(f"| Food & Dining | {b.food_cost:,.2f} |")
        lines.append(f"| Local Transportation | {b.local_transport_cost:,.2f} |")
        lines.append(f"| Activities & Tours | {b.activities_cost:,.2f} |")
        lines.append(f"| Miscellaneous | {b.misc_cost:,.2f} |")
        lines.append(f"| Emergency Buffer (7%) | {b.emergency_buffer:,.2f} |")
        lines.append(f"| **Total Estimated Budget** | **{b.total_budget:,.2f}** |")
        lines.append(f"| **Per Person Cost** | **{b.per_person_cost:,.2f}** |")
        lines.append(f"")

    # Itinerary
    if trip.itinerary:
        lines.append(f"## 📅 Day-by-Day Itinerary")
        for day in trip.itinerary.days:
            lines.append(f"### Day {day.day_number}: {day.theme}")
            lines.append(f"- **Morning ({day.morning.get('time', 'Morning')})**: {day.morning.get('activity')} (*{day.morning.get('location')}*)")
            lines.append(f"- **Afternoon ({day.afternoon.get('time', 'Afternoon')})**: {day.afternoon.get('activity')} (*{day.afternoon.get('location')}*)")
            lines.append(f"- **Evening ({day.evening.get('time', 'Evening')})**: {day.evening.get('activity')} (*{day.evening.get('location')}*)")
            lines.append(f"- **Estimated Daily Spend**: {trip.currency} {day.estimated_daily_spend:,.2f}")
            lines.append(f"- **Transport Notes**: {day.transport_notes}")
            lines.append(f"")

    # Sources
    if trip.sources:
        lines.append(f"## 🔍 Research Sources & Citations")
        for s in trip.sources:
            lines.append(f"- [{s.title}]({s.url or '#'}) - Agent: *{s.agent_name}*")

    lines.append(f"\n---")
    lines.append(f"*Generated by VoyageAI — Your intelligent team of AI travel agents.*")
    return "\n".join(lines)


@router.get("/markdown")
def export_markdown(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    md_content = _generate_markdown_doc(trip)
    filename = f"VoyageAI_{trip.destination.replace(' ', '_')}_{trip.duration_days}Days.md"

    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/print", response_class=HTMLResponse)
def export_print_html(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    md = _generate_markdown_doc(trip)
    # Simple clean print HTML formatting
    html_lines = []
    for line in md.split("\n"):
        if line.startswith("# "):
            html_lines.append(f"<h1 style='color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px;'>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2 style='color: #1e40af; margin-top: 24px;'>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3 style='color: #2563eb;'>{line[4:]}</h3>")
        elif line.startswith("- "):
            html_lines.append(f"<li style='margin-bottom: 4px;'>{line[2:]}</li>")
        elif line.strip() == "":
            html_lines.append("<br/>")
        else:
            html_lines.append(f"<p>{line}</p>")

    body_content = "\n".join(html_lines)
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>VoyageAI - {trip.title}</title>
    <meta charset="utf-8"/>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 860px; margin: 40px auto; padding: 0 20px; color: #1e293b; }}
        @media print {{
            body {{ max-width: 100%; margin: 20px; }}
            .no-print {{ display: none; }}
        }}
        .print-btn {{ background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; margin-bottom: 24px; }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="print-btn" onclick="window.print()">🖨️ Print or Save as PDF</button>
    </div>
    {body_content}
</body>
</html>"""
    return HTMLResponse(content=full_html)


@router.get("/pdf")
def export_pdf(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Draw header banner
    p.setFillColor(colors.HexColor("#1e3a8a"))
    p.rect(0, height - 80, width, 80, fill=1, stroke=0)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(40, height - 45, "VoyageAI - Travel Itinerary")
    p.setFont("Helvetica", 10)
    p.drawString(40, height - 65, "Your intelligent team of AI travel agents")

    p.setFillColor(colors.black)
    y = height - 110

    # Trip Metadata
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, f"{trip.title}")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Destination: {trip.destination}  |  Duration: {trip.duration_days} Days  |  Travelers: {trip.travellers}")
    y -= 15
    budget_txt = f"Budget: {trip.currency} {trip.budget:,.0f}" if trip.budget else "Budget: Flexible"
    p.drawString(40, y, f"{budget_txt}  |  Style: {trip.travel_style}")
    y -= 30

    # Summary
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Overview & Strategy:")
    y -= 18
    p.setFont("Helvetica", 9)
    summary_txt = trip.summary or "Multi-agent optimized schedule balancing cultural landmarks and realistic transit."
    p.drawString(40, y, summary_txt[:100] + ("..." if len(summary_txt) > 100 else ""))
    y -= 30

    # Itinerary days preview
    if trip.itinerary and trip.itinerary.days:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(40, y, "Schedule Summary:")
        y -= 20
        p.setFont("Helvetica", 9)
        for day in trip.itinerary.days[:6]:
            if y < 80:
                p.showPage()
                y = height - 60
            p.drawString(40, y, f"Day {day.day_number}: {day.theme}")
            y -= 15

    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(colors.gray)
    p.drawString(40, 40, f"Generated for {current_user.username} by VoyageAI Multi-Agent System.")

    p.save()
    buffer.seek(0)

    filename = f"VoyageAI_{trip.destination.replace(' ', '_')}.pdf"
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
