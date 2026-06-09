import pytest
from llm_scoring.config import LLMScoringConfig
from llm_scoring.models import TrackingMode


def test_config_defaults():
    config = LLMScoringConfig(scoring_url="http://localhost:8080")
    assert config.mode == TrackingMode.SLIDING_WINDOW
    assert config.window_size == 5
    assert config.timeout_seconds == 10
    assert config.max_retries == 3
    assert config.silent_on_error is True
    assert config.default_scenario is None


def test_config_custom_values():
    config = LLMScoringConfig(
        scoring_url="http://scoring-service",
        default_scenario="return-agent",
        mode=TrackingMode.FULL_CONVERSATION,
        window_size=3,
        timeout_seconds=30,
        max_retries=5,
        silent_on_error=False,
    )
    assert config.default_scenario == "return-agent"
    assert config.mode == TrackingMode.FULL_CONVERSATION
    assert config.window_size == 3
    assert config.silent_on_error is False
