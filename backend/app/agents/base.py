import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic for the agent. Context contains trip details and research from prior agents."""
        pass

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper around run with timing, metrics, and error handling."""
        start_time = time.time()
        logger.info(f"Agent [{self.name}] starting execution.")
        try:
            result = await self.run(context)
            duration = round(time.time() - start_time, 2)
            logger.info(f"Agent [{self.name}] completed successfully in {duration}s.")
            return {
                "agent_name": self.name,
                "status": "completed",
                "duration_seconds": duration,
                "data": result,
                "error": None,
            }
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            logger.error(f"Agent [{self.name}] failed after {duration}s: {e}", exc_info=True)
            return {
                "agent_name": self.name,
                "status": "failed",
                "duration_seconds": duration,
                "data": None,
                "error": str(e),
            }
