from dataclasses import dataclass, field
from llm_scoring.models import TrackingMode


@dataclass
class LLMScoringConfig:
    # URL of the scoring service
    scoring_url: str

    # Default scenario name
    default_scenario: str = None

    # Tracking mode
    mode: TrackingMode = TrackingMode.SLIDING_WINDOW

    # Window size for SLIDING_WINDOW mode
    window_size: int = 5

    # HTTP timeout in seconds
    timeout_seconds: int = 10

    # Max retries on failure
    max_retries: int = 3

    # If True — swallow errors silently
    silent_on_error: bool = True
