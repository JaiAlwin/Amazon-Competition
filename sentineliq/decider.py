"""Small client for the hosted Strands Decider 2B HTTP API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class DeciderError(RuntimeError):
    """Raised when the Decider API cannot return a valid response."""


@dataclass(frozen=True)
class DeciderClient:
    base_url: str
    api_key: str
    timeout: float = 30.0

    @classmethod
    def from_environment(cls) -> "DeciderClient":
        try:
            return cls(os.environ["DECIDER_URL"], os.environ["DECIDER_API_KEY"])
        except KeyError as exc:
            raise DeciderError(f"Missing required environment variable: {exc.args[0]}") from exc

    def decide(self, state: str, questions: dict) -> dict:
        payload = json.dumps({"state": state, "questions": questions}).encode("utf-8")
        request = Request(
            f"{self.base_url.rstrip('/')}/v1/decide",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise DeciderError(f"Decider request failed: {exc}") from exc
        if not isinstance(body, dict) or not isinstance(body.get("answers"), dict):
            raise DeciderError("Decider response did not contain an answers object")
        return body["answers"]
