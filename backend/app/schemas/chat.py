from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, computed_field


class ChatMessageRequest(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender: str
    content: str
    actions_taken: Optional[Dict[str, Any]] = None
    created_at: datetime

    @computed_field
    @property
    def sources(self) -> List[Dict[str, Any]]:
        if self.actions_taken:
            return self.actions_taken.get("sources", [])
        return []


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    messages: List[ChatMessageResponse] = []
    created_at: datetime
