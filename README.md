# LLM Scoring Service — Python SDK

Python SDK for [LLM Scoring Service](https://github.com/nishanthr878/llm-scoring-service).

## Install

**Option 1 — Directly from GitHub (recommended for now)**

```bash
pip install git+https://github.com/nishanthr878/llm-scoring-service-python-sdk.git
```

**Option 2 — From source**

```bash
git clone https://github.com/nishanthr878/llm-scoring-service-python-sdk
cd llm-scoring-service-python-sdk
pip install -e .
```

## Quick Start

```python
from llm_scoring import LLMScoring, LLMScoringConfig, TrackingMode

# Configure once at startup
scoring = LLMScoring.create(LLMScoringConfig(
    scoring_url="http://localhost:8080",
    default_scenario="return-agent",
    mode=TrackingMode.SLIDING_WINDOW,
    window_size=5,
    silent_on_error=True,
))

# Create tracker per session
tracker = scoring.session(session_id, "return-agent", model_name)

# Call after every bot response — non-blocking
tracker.track(user_message, bot_response)
```

## LangChain Integration

Zero code change — just add the callback:

```python
from llm_scoring.langchain_callback import LLMScoringCallback
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(callbacks=[
    LLMScoringCallback(
        scoring_url="http://localhost:8080",
        scenario_name="return-agent",
        model_name="gpt-4"
    )
])

# Every call auto-tracked — no other code change needed
response = llm.invoke("I want to return my order")
```

## Context Manager

```python
# Automatically submits full conversation on exit
with scoring.session(session_id) as tracker:
    tracker.track(user_message_1, bot_response_1)
    tracker.track(user_message_2, bot_response_2)
```

## Synchronous (for tests)

```python
result = tracker.track_and_wait(user_message, bot_response)
assert result.overall_passed is True
```

## Tracking Modes

| Mode | Behavior | Best for |
|------|----------|----------|
| `TURN_BY_TURN` | Latest turn only | Low latency |
| `SLIDING_WINDOW` | Last N turns (default) | Most use cases |
| `FULL_CONVERSATION` | Full history | Short conversations |

## Configuration Reference

| Option | Default | Description |
|--------|---------|-------------|
| `scoring_url` | required | URL of scoring service |
| `default_scenario` | None | Default scenario name |
| `mode` | `SLIDING_WINDOW` | Tracking mode |
| `window_size` | 5 | Turns in sliding window |
| `timeout_seconds` | 10 | HTTP timeout |
| `max_retries` | 3 | Retry attempts |
| `silent_on_error` | True | Swallow errors silently |

## Supported Response Object

```python
result.id               # scoring result ID
result.session_id       # session ID
result.overall_passed   # True / False / None (inconclusive)
result.scores           # {"faithfulness": 0.9, ...}
result.reasoning        # {"faithfulness": "...", ...}
result.passed           # {"faithfulness": True, ...}
result.flag_reasons     # "policyCompliance failed: ..." or None
result.scored_at        # ISO timestamp
```

## Requirements

- Python 3.9+
- LLM Scoring Service running and accessible

## Related

- [LLM Scoring Service](https://github.com/nishanthr878/llm-scoring-service)
- [Java SDK](https://github.com/nishanthr878/llm-scoring-service-java-sdk)
- [UI](https://github.com/nishanthr878/llm-scoring-service-ui)

