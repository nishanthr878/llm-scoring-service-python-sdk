from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any


class TrackingMode(Enum):
    TURN_BY_TURN = "turn_by_turn"
    SLIDING_WINDOW = "sliding_window"
    FULL_CONVERSATION = "full_conversation"


@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str

    @staticmethod
    def user(content: str) -> "ChatMessage":
        return ChatMessage(role="user", content=content)

    @staticmethod
    def assistant(content: str) -> "ChatMessage":
        return ChatMessage(role="assistant", content=content)

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class ScoringResponse:
    id: Optional[int] = None
    session_id: Optional[str] = None
    type: Optional[str] = None
    scores: Optional[Dict[str, float]] = None
    reasoning: Optional[Dict[str, str]] = None
    passed: Optional[Dict[str, bool]] = None
    overall_passed: Optional[bool] = None
    flag_reasons: Optional[str] = None
    scored_at: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ScoringResponse":
        return ScoringResponse(
            id=data.get("id"),
            session_id=data.get("sessionId"),
            type=data.get("type"),
            scores=data.get("scores"),
            reasoning=data.get("reasoning"),
            passed=data.get("passed"),
            overall_passed=data.get("overallPassed"),
            flag_reasons=data.get("flagReasons"),
            scored_at=data.get("scoredAt"),
        )
