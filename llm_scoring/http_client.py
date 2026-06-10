import time
import requests
from typing import Optional
from llm_scoring.models import ScoringResponse


class ScoringHttpClient:

    def __init__(self, base_url: str, timeout_seconds: int, max_retries: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def ingest(self, payload: dict) -> None:
        """Fire and forget — async ingest via Kafka."""
        url = f"{self.base_url}/api/v1/events/ingest"
        self._request(url, payload, expected_status=202)

    def ingest_sync(self, payload: dict) -> Optional[ScoringResponse]:
        """Synchronous ingest — waits for scoring result."""
        url = f"{self.base_url}/api/v1/events/ingest?sync=true"
        data = self._request(url, payload, expected_status=200)
        if data:
            return ScoringResponse.from_dict(data)
        return None

    def _request(self, url: str, payload: dict,
                 expected_status: int) -> Optional[dict]:
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    url, json=payload, timeout=self.timeout)

                if response.status_code == expected_status:
                    if response.content:
                        return response.json()
                    return None

                raise RuntimeError(
                    f"Unexpected status {response.status_code}: {response.text}")

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(0.5 * attempt)

        raise RuntimeError(
            f"Failed after {self.max_retries} attempts: {last_exception}")

    def close(self):
        self.session.close()
