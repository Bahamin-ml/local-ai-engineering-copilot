from __future__ import annotations

from typing import Any, Dict, Iterator, Optional
import httpx
import json

from desktop.core.config import DesktopConfig


class SSEClient:
    """
    Minimal SSE client for 'text/event-stream' where each message line begins with 'data: '.
    """

    def __init__(self, config: Optional[DesktopConfig] = None):
        self.config = config or DesktopConfig()

    def stream_chat(self, payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        url = self.config.api_base_url + self.config.stream_endpoint

        with httpx.Client(timeout=None) as client:
            with client.stream("POST", url, json=payload, headers={"Accept": "text/event-stream"}) as r:
                r.raise_for_status()

                for line in r.iter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[len("data: "):].strip()
                        try:
                            yield json.loads(data_str)
                        except json.JSONDecodeError:
                            yield {"event": "error", "message": f"Invalid JSON SSE frame: {data_str}"}
