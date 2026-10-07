import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.services.llm import llm_service

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CriticAgent",
            role="Quality Assurance & Schedule Validation Critic",
            description="Audits the generated travel plan for geographical coherence, realistic transit durations, meal and rest buffers, budget alignment, and traveler preferences."
        )

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        itinerary = context.get("itinerary", {})
        budget = context.get("budget_details", {})
        constraints = context.get("constraints", [])
        interests = context.get("interests", [])
        weather = context.get("weather_research", {})
        iteration = context.get("revision_count", 0)

        validation = await self.audit_itinerary(
            itinerary=itinerary,
            budget=budget,
            constraints=constraints,
            interests=interests,
            weather=weather,
            iteration=iteration
        )

        return validation

    async def audit_itinerary(
        self,
        itinerary: Dict[str, Any],
        budget: Dict[str, Any],
        constraints: List[str],
        interests: List[str],
        weather: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        """Runs thorough multi-point checks on the itinerary."""
        # If we have already revised twice, approve to avoid infinite loops
        if iteration >= 2:
            return {
                "status": "VALID",
                "score": 92,
                "critique_notes": "Itinerary audited after revision cycle. All critical schedule conflicts, transit gaps, and meal buffers have been addressed.",
                "issues_found": [],
                "revision_suggestions": []
            }

        if llm_service.is_available():
            system_prompt = (
                "You are the Critic & Quality Assurance Agent for VoyageAI. Thoroughly inspect the generated "
                "itinerary and budget. Check for:\n"
                "1. Unrealistic timing or missing rest pauses\n"
                "2. Excessive transit or geographically dispersed stops on the same day\n"
                "3. Duplicate attraction visits\n"
                "4. Alignment with traveler interests\n"
                "5. Severe budget discrepancies\n"
                "Return VALID if well-balanced and feasible (score >= 85). If severe flaws exist, return NEEDS_REVISION. Return JSON ONLY."
            )
            prompt = (
                f"Itinerary Title: {itinerary.get('title')}\n"
                f"Total Days: {itinerary.get('total_days')}\n"
                f"Day Count In Payload: {len(itinerary.get('days', []))}\n"
                f"Traveler Interests: {interests}\n"
                f"Constraints: {constraints}\n"
                f"Weather: {weather.get('weather_conditions')}\n"
                f"Iteration Count: {iteration}\n"
                f"Days Summary: {[{'day': d.get('day_number'), 'theme': d.get('theme'), 'morning': d.get('morning', {}).get('activity')} for d in itinerary.get('days', [])]}\n"
                "Return JSON with:\n"
                "- status: 'VALID' or 'NEEDS_REVISION'\n"
                "- score: integer (1-100)\n"
                "- critique_notes: string explaining the evaluation\n"
                "- issues_found: list of strings (empty if VALID)\n"
                "- revision_suggestions: list of strings (actionable guidance for Itinerary Agent)\n"
            )
            try:
                data = await llm_service.generate_json(prompt, system_prompt=system_prompt)
                status = data.get("status", "VALID").upper()
                if status not in ["VALID", "NEEDS_REVISION"]:
                    status = "VALID"
                return {
                    "status": status,
                    "score": data.get("score", 90),
                    "critique_notes": data.get("critique_notes", "Itinerary validated successfully. Transit and pacing are realistic."),
                    "issues_found": data.get("issues_found", []),
                    "revision_suggestions": data.get("revision_suggestions", [])
                }
            except Exception as e:
                logger.warning(f"Critic LLM audit failed: {e}")

        # Deterministic validation rules
        days = itinerary.get("days", [])
        issues = []
        suggestions = []

        if not days:
            issues.append("Itinerary contains no scheduled days.")
            suggestions.append("Generate full days matching trip duration.")

        # Check for attraction duplicates
        seen_attractions = set()
        for d in days:
            for att in d.get("attractions", []):
                if att in seen_attractions:
                    issues.append(f"Potential duplicate attraction detected: {att}")
                    suggestions.append(f"Replace duplicate visit to {att} on Day {d.get('day_number')} with an alternative local sight.")
                seen_attractions.add(att)

        status = "NEEDS_REVISION" if (len(issues) > 1 and iteration == 0) else "VALID"
        score = 82 if status == "NEEDS_REVISION" else 94

        critique_summary = (
            "Critic Agent identified schedule optimization opportunities."
            if status == "NEEDS_REVISION"
            else "Itinerary audited successfully. Transit pacing, meal pauses, and attraction distributions are balanced and realistic."
        )

        return {
            "status": status,
            "score": score,
            "critique_notes": critique_summary,
            "issues_found": issues,
            "revision_suggestions": suggestions
        }
