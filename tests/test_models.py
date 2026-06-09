import pytest
from llm_scoring.models import ChatMessage, TrackingMode, ScoringResponse


def test_chat_message_user_factory():
    msg = ChatMessage.user("Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_chat_message_assistant_factory():
    msg = ChatMessage.assistant("Hi there")
    assert msg.role == "assistant"
    assert msg.content == "Hi there"


def test_chat_message_to_dict():
    msg = ChatMessage.user("Hello")
    d = msg.to_dict()
    assert d == {"role": "user", "content": "Hello"}


def test_tracking_mode_values():
    assert TrackingMode.TURN_BY_TURN.value == "turn_by_turn"
    assert TrackingMode.SLIDING_WINDOW.value == "sliding_window"
    assert TrackingMode.FULL_CONVERSATION.value == "full_conversation"


def test_scoring_response_from_dict():
    data = {
        "id": 1,
        "sessionId": "test-session",
        "type": "SCENARIO",
        "scores": {"faithfulness": 0.9},
        "reasoning": {"faithfulness": "Good"},
        "passed": {"faithfulness": True},
        "overallPassed": True,
        "flagReasons": None,
        "scoredAt": "2026-06-07T12:00:00Z",
    }
    response = ScoringResponse.from_dict(data)
    assert response.id == 1
    assert response.session_id == "test-session"
    assert response.overall_passed is True
    assert response.scores["faithfulness"] == 0.9


def test_scoring_response_from_empty_dict():
    response = ScoringResponse.from_dict({})
    assert response.id is None
    assert response.overall_passed is None
