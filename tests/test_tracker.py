import pytest
from unittest.mock import MagicMock, patch
from llm_scoring.client import LLMScoring
from llm_scoring.config import LLMScoringConfig
from llm_scoring.models import TrackingMode, ChatMessage
from llm_scoring.tracker.conversation_tracker import ConversationTracker
from llm_scoring.http_client import ScoringHttpClient


def make_config(mode=TrackingMode.SLIDING_WINDOW, window_size=2):
    return LLMScoringConfig(
        scoring_url="http://localhost:8080",
        default_scenario="return-agent",
        mode=mode,
        window_size=window_size,
        silent_on_error=True,
    )


def make_tracker(config, mock_client=None):
    if mock_client is None:
        mock_client = MagicMock(spec=ScoringHttpClient)
    return ConversationTracker(
        config=config,
        http_client=mock_client,
        session_id="test-session",
        scenario_name="return-agent",
        model_name="test-model",
    )


def test_tracker_sliding_window_sends_last_n_turns():
    config = make_config(mode=TrackingMode.SLIDING_WINDOW, window_size=2)
    mock_client = MagicMock(spec=ScoringHttpClient)
    mock_client.ingest.return_value = None
    tracker = make_tracker(config, mock_client)

    # Add 3 turns (6 messages)
    tracker.track("q1", "a1")
    tracker.track("q2", "a2")
    tracker.track("q3", "a3")

    # Wait for async thread
    import time
    time.sleep(0.1)

    # Last call should have window_size * 2 = 4 messages
    last_call = mock_client.ingest.call_args
    payload = last_call[0][0]
    assert len(payload["messages"]) == 4


def test_tracker_turn_by_turn_sends_only_last_turn():
    config = make_config(mode=TrackingMode.TURN_BY_TURN)
    mock_client = MagicMock(spec=ScoringHttpClient)
    mock_client.ingest.return_value = None
    tracker = make_tracker(config, mock_client)

    tracker.track("q1", "a1")
    tracker.track("q2", "a2")

    import time
    time.sleep(0.1)

    last_call = mock_client.ingest.call_args
    payload = last_call[0][0]
    assert len(payload["messages"]) == 2
    assert payload["messages"][0]["content"] == "q2"
    assert payload["messages"][1]["content"] == "a2"


def test_tracker_full_conversation_sends_all():
    config = make_config(mode=TrackingMode.FULL_CONVERSATION)
    mock_client = MagicMock(spec=ScoringHttpClient)
    mock_client.ingest.return_value = None
    tracker = make_tracker(config, mock_client)

    tracker.track("q1", "a1")
    tracker.track("q2", "a2")
    tracker.track("q3", "a3")

    import time
    time.sleep(0.1)

    last_call = mock_client.ingest.call_args
    payload = last_call[0][0]
    assert len(payload["messages"]) == 6


def test_tracker_payload_structure():
    config = make_config()
    mock_client = MagicMock(spec=ScoringHttpClient)
    mock_client.ingest.return_value = None
    tracker = make_tracker(config, mock_client)

    tracker.track("Hello", "Hi there")

    import time
    time.sleep(0.1)

    payload = mock_client.ingest.call_args[0][0]
    assert payload["sessionId"] == "test-session"
    assert payload["scenarioName"] == "return-agent"
    assert payload["modelName"] == "test-model"
    assert payload["format"] == "openai"
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][1]["role"] == "assistant"


def test_llm_scoring_creates_tracker():
    config = make_config()
    scoring = LLMScoring.create(config)
    tracker = scoring.session("session-123")
    assert tracker is not None
    assert tracker.session_id == "session-123"


def test_llm_scoring_session_with_scenario_override():
    config = make_config()
    scoring = LLMScoring.create(config)
    tracker = scoring.session("session-123", "support-agent")
    assert tracker.scenario_name == "support-agent"


def test_context_manager_usage():
    config = make_config()
    mock_client = MagicMock(spec=ScoringHttpClient)
    mock_client.ingest.return_value = None

    with ConversationTracker(
        config=config,
        http_client=mock_client,
        session_id="ctx-session",
    ) as tracker:
        tracker.history.append(ChatMessage.user("Hello"))
        tracker.history.append(ChatMessage.assistant("Hi"))

    import time
    time.sleep(0.1)
    assert mock_client.ingest.called
