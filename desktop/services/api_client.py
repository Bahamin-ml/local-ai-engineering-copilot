from __future__ import annotations

from typing import Any, Dict, Optional
import httpx

from desktop.core.config import DesktopConfig


class ApiClient:
    def __init__(self, config: Optional[DesktopConfig] = None):
        self.config = config or DesktopConfig()

    def chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self.config.api_base_url + self.config.chat_endpoint
        with httpx.Client(timeout=self.config.request_timeout_s) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            return r.json()
