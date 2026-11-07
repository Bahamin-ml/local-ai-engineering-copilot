"""
Background QThread Worker for SSE Streaming Chat via FastAPI backend.
"""

import json
from PyQt5.QtCore import QThread, pyqtSignal
import httpx


class ChatStreamWorker(QThread):
    # Signals
    token_received = pyqtSignal(str)
    stream_started = pyqtSignal(dict)
    stream_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        base_url: str,
        query: str,
        session_id: str,
        mode: str,
        use_rag: bool,
    ):
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.query = query
        self.session_id = session_id
        self.mode = mode
        self.use_rag = use_rag
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        endpoint = f"{self.base_url}/api/chat/stream"
        payload = {
            "query": self.query,
            "session_id": self.session_id,
            "mode": self.mode,
            "use_rag": self.use_rag,
        }

        full_response = []
        try:
            with httpx.Client(timeout=None) as client:
                with client.stream("POST", endpoint, json=payload) as response:
                    if response.status_code != 200:
                        self.error_occurred.emit(f"Server returned status {response.status_code}")
                        return

                    for line in response.iter_lines():
                        if self._is_cancelled:
                            break

                        if not line or not line.startswith("data: "):
                            continue

                        data_str = line[6:].strip()
                        try:
                            event_data = json.loads(data_str)
                            event_type = event_data.get("event")

                            if event_type == "start":
                                self.stream_started.emit(event_data)
                            elif event_type == "chunk":
                                content = event_data.get("content", "")
                                full_response.append(content)
                                self.token_received.emit(content)
                            elif event_type == "end":
                                break
                            elif event_type == "error":
                                self.error_occurred.emit(event_data.get("message", "Unknown error"))
                                return
                        except json.JSONDecodeError:
                            continue

            self.stream_finished.emit("".join(full_response))
        except Exception as e:
            self.error_occurred.emit(str(e))
