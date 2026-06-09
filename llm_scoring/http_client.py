import time
import requests
from typing import Optional, List, Dict
from llm_scoring.models import ScoringResponse


class ScoringHttpClient:

    def __init__(self, base_url: str, timeout_seconds: int, max_retries: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def ingest(self, payload: Dict) -> Optional[ScoringResponse]:
        url = f"{self.base_url}/api/v1/events/ingest"
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code == 202:
                    # Async accepted
                    return None

                if response.status_code == 200:
                    return ScoringResponse.from_dict(response.json())

                raise RuntimeError(
                    f"Unexpected status {response.status_code}: {response.text}"
                )

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(0.5 * attempt)

        raise RuntimeError(
            f"Failed after {self.max_retries} attempts: {last_exception}"
        )

    def close(self):
        self.session.close()
