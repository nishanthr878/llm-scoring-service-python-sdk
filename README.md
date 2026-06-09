# LLM Scoring Service — Python SDK

Python SDK for [LLM Scoring Service](https://github.com/nishanthr878/llm-scoring-service).

## Install

```bash
pip install llm-scoring-sdk
```

## Quick Start

```python
from llm_scoring import LLMScoring, LLMScoringConfig, TrackingMode

scoring = LLMScoring.create(LLMScoringConfig(
    scoring_url="http://localhost:8080",
    default_scenario="return-agent",
    mode=TrackingMode.SLIDING_WINDOW,
    window_size=5,
))

tracker = scoring.session(session_id, "return-agent", model_name)
tracker.track(user_message, bot_response)  # non-blocking
```

## LangChain Integration

Zero code change — just add the callback:

```python
from llm_scoring.langchain_callback import LLMScoringCallback
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(callbacks=[
    LLMScoringCallback(
        scoring_url="http://localhost:8080",
        scenario_name="return-agent"
    )
])

# Every call auto-tracked
response = llm.invoke("I want to return my order")
```

## Context Manager

```python
with scoring.session(session_id) as tracker:
    tracker.track(user_message, bot_response)
# Automatically submits on exit
```

## Tracking Modes

| Mode | Behavior |
|------|----------|
| `TURN_BY_TURN` | Latest turn only |
| `SLIDING_WINDOW` | Last N turns (default) |
| `FULL_CONVERSATION` | Full history |

## Requirements

Python 3.9+
