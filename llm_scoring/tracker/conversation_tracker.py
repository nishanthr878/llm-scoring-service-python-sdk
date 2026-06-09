import threading
from typing import Optional, List, Callable
from llm_scoring.models import ChatMessage, TrackingMode, ScoringResponse
from llm_scoring.http_client import ScoringHttpClient
from llm_scoring.config import LLMScoringConfig


class ConversationTracker:

    def __init__(
        self,
        config: LLMScoringConfig,
        http_client: ScoringHttpClient,
        session_id: str,
        scenario_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.config = config
        self.http_client = http_client
        self.session_id = session_id
        self.scenario_name = scenario_name or config.default_scenario
        self.model_name = model_name
        self.history: List[ChatMessage] = []
        self._on_complete: Optional[Callable[[ScoringResponse], None]] = None

    def on_complete(self, callback: Callable[[ScoringResponse], None]) -> "ConversationTracker":
        self._on_complete = callback
        return self

    def track(self, user_message: str, assistant_response: str) -> None:
        """Fire and forget — non-blocking."""
        self.history.append(ChatMessage.user(user_message))
        self.history.append(ChatMessage.assistant(assistant_response))

        messages = self._resolve_messages()
        payload = self._build_payload(messages)

        thread = threading.Thread(
            target=self._submit,
            args=(payload,),
            daemon=True
        )
        thread.start()

    def track_and_wait(
        self, user_message: str, assistant_response: str
    ) -> Optional[ScoringResponse]:
        """Synchronous — blocks until scoring completes. Useful for tests."""
        self.history.append(ChatMessage.user(user_message))
        self.history.append(ChatMessage.assistant(assistant_response))

        messages = self._resolve_messages()
        payload = self._build_payload(messages)

        return self._submit_sync(payload)

    def submit_all(self) -> None:
        """Submit full conversation history."""
        payload = self._build_payload(list(self.history))
        thread = threading.Thread(
            target=self._submit,
            args=(payload,),
            daemon=True
        )
        thread.start()

    # Context manager support — use with `with` statement
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.submit_all()
        return False

    def _resolve_messages(self) -> List[ChatMessage]:
        mode = self.config.mode

        if mode == TrackingMode.TURN_BY_TURN:
            return self.history[-2:]

        elif mode == TrackingMode.SLIDING_WINDOW:
            window = self.config.window_size * 2
            return self.history[-window:]

        else:  # FULL_CONVERSATION
            return list(self.history)

    def _build_payload(self, messages: List[ChatMessage]) -> dict:
        return {
            "sessionId": self.session_id,
            "scenarioName": self.scenario_name,
            "modelName": self.model_name,
            "format": "openai",
            "messages": [m.to_dict() for m in messages],
        }

    def _submit(self, payload: dict) -> None:
        try:
            result = self.http_client.ingest(payload)
            if result and self._on_complete:
                self._on_complete(result)
        except Exception as e:
            self._handle_error(e)

    def _submit_sync(self, payload: dict) -> Optional[ScoringResponse]:
        try:
            return self.http_client.ingest(payload)
        except Exception as e:
            self._handle_error(e)
            return None

    def _handle_error(self, e: Exception) -> None:
        if self.config.silent_on_error:
            print(f"[LLMScoring SDK] Error: {e}")
        else:
            raise RuntimeError(f"[LLMScoring SDK] Failed to submit") from e
