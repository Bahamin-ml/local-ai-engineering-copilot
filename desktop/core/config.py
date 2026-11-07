from pydantic import BaseModel


class DesktopConfig(BaseModel):
    api_base_url: str = "http://127.0.0.1:8000"
    chat_endpoint: str = "/api/chat"
    stream_endpoint: str = "/api/chat/stream"
    sessions_endpoint: str = "/api/sessions"
    request_timeout_s: float = 60.0
