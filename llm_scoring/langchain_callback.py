from typing import Any, Dict, List, Optional, Union
from llm_scoring.client import LLMScoring
from llm_scoring.config import LLMScoringConfig


class LLMScoringCallback:
    """
    LangChain callback handler — auto-tracks every LLM call.

    Usage:
        from llm_scoring.langchain_callback import LLMScoringCallback
        from langchain_openai import ChatOpenAI

        callback = LLMScoringCallback(
            scoring_url="http://your-scoring-service",
            scenario_name="return-agent"
        )

        llm = ChatOpenAI(callbacks=[callback])

        # Every call auto-tracked — no other code change
        response = llm.invoke("I want to return my order")
    """

    def __init__(
        self,
        scoring_url: str,
        scenario_name: str,
        model_name: str = "unknown",
        silent_on_error: bool = True,
    ):
        self.scoring = LLMScoring.create(LLMScoringConfig(
            scoring_url=scoring_url,
            default_scenario=scenario_name,
            silent_on_error=silent_on_error,
        ))
        self.model_name = model_name
        self.scenario_name = scenario_name
        self._last_input: Optional[str] = None

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        # Store the last user input
        if prompts:
            self._last_input = prompts[-1]

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        if self._last_input is None:
            return

        try:
            # Extract assistant response from LangChain response object
            output = response.generations[0][0].text
            session_id = kwargs.get("run_id", "unknown")

            tracker = self.scoring.session(
                str(session_id),
                self.scenario_name,
                self.model_name
            )
            tracker.track(self._last_input, output)
        except Exception as e:
            print(f"[LLMScoring Callback] Error: {e}")
        finally:
            self._last_input = None

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        self._last_input = None
