import json
import logging
import re
from typing import Any, Dict, Optional
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
        self.client = None
        if self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"):
            try:
                self.client = Groq(api_key=self.api_key.strip())
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = "You are an expert travel planning AI assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        if not self.is_available():
            raise ValueError("Groq API key not configured or client initialization failed.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise e

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str = "You are an expert travel planning AI assistant. Return valid JSON only.",
        temperature: float = 0.3,
        max_tokens: int = 3000,
    ) -> Dict[str, Any]:
        json_instruction = (
            "\nCRITICAL: Respond ONLY with a valid, parseable JSON object. "
            "Do not include any introductory remarks, markdown code blocks (```json), "
            "or trailing text outside the JSON structure."
        )
        combined_prompt = prompt + json_instruction

        if not self.is_available():
            raise ValueError("Groq API key not configured.")

        raw_output = await self.generate_text(
            prompt=combined_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return self.parse_json_safely(raw_output)

    @staticmethod
    def parse_json_safely(raw_text: str) -> Dict[str, Any]:
        """Safely parses JSON from LLM output, stripping markdown fences and searching brackets."""
        cleaned = raw_text.strip()
        # Remove ```json and ``` fences if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract the first { ... } or [ ... ]
            match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            logger.error(f"Failed to parse LLM JSON: {raw_text[:200]}...")
            raise ValueError(f"Could not parse valid JSON from LLM response: {cleaned[:100]}...")


llm_service = LLMService()
