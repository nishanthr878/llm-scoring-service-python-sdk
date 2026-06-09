from llm_scoring.config import LLMScoringConfig
from llm_scoring.http_client import ScoringHttpClient
from llm_scoring.tracker.conversation_tracker import ConversationTracker
from typing import Optional


class LLMScoring:

    def __init__(self, config: LLMScoringConfig):
        self.config = config
        self._http_client = ScoringHttpClient(
            base_url=config.scoring_url,
            timeout_seconds=config.timeout_seconds,
            max_retries=config.max_retries,
        )

    @staticmethod
    def create(config: LLMScoringConfig) -> "LLMScoring":
        return LLMScoring(config)

    def session(
        self,
        session_id: str,
        scenario_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> ConversationTracker:
        return ConversationTracker(
            config=self.config,
            http_client=self._http_client,
            session_id=session_id,
            scenario_name=scenario_name,
            model_name=model_name,
        )

    def close(self):
        self._http_client.close()

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
