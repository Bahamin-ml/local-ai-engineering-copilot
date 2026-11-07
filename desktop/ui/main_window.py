# desktop/ui/main_window.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from desktop.services.session_store import SessionStore
from desktop.services.sse_client import SSEClient
from desktop.ui.widgets.chat_input import ChatInput
from desktop.ui.widgets.chat_view import ChatView
from desktop.ui.widgets.session_sidebar import SessionSidebar
from desktop.ui.widgets.top_bar import TopBar


@dataclass
class PendingChat:
    """A new conversation waiting for the backend to return its session ID."""

    first_user_text: str
    created_at: str


class StreamWorker(QThread):
    """Runs the SSE request in a background thread."""

    event_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    stream_finished = pyqtSignal()

    def __init__(self, payload: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.payload = payload
        self.client = SSEClient()

    def run(self) -> None:
        try:
            for event in self.client.stream_chat(self.payload):
                if isinstance(event, dict):
                    self.event_received.emit(event)
        except Exception as exc:
            self.error_occurred.emit(str(exc))
        finally:
            self.stream_finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ML Engineering Copilot")
        self.resize(1280, 820)
        self.setMinimumSize(960, 640)

        self.active_session_id: Optional[str] = None
        self.pending_chat: Optional[PendingChat] = None
        self.pending_user_message: Optional[str] = None
        self.current_assistant_response = ""
        self.worker: Optional[StreamWorker] = None

        self.sidebar = SessionSidebar()
        self.topbar = TopBar()
        self.chat = ChatView()
        self.chat_input = ChatInput()

        self._build_layout()
        self._init_store()
        self._connect_signals()
        self.reload_sessions()

        self.chat_input.setFocus()

    # ------------------------------------------------------------------
    # Layout and initialization
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        central_widget = QWidget(self)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)
        content_layout.addWidget(self.topbar)
        content_layout.addWidget(self.chat, 1)
        content_layout.addWidget(self.chat_input)

        root_layout.addWidget(self.sidebar)
        root_layout.addLayout(content_layout, 1)

        self.setCentralWidget(central_widget)

    def _init_store(self) -> None:
        data_dir = Path(__file__).resolve().parents[1] / "data"
        self.store = SessionStore(db_path=data_dir / "desktop.db")

    def _connect_signals(self) -> None:
        self.chat_input.message_submitted.connect(self.on_submit_message)

        self.sidebar.new_requested.connect(self.on_new_chat)
        self.sidebar.delete_requested.connect(self.on_delete_chat)
        self.sidebar.selected.connect(self.on_select_chat)

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _set_busy(self, busy: bool) -> None:
        self.chat_input.setEnabled(not busy)
        self.sidebar.setEnabled(not busy)

        if not busy:
            self.chat_input.setFocus()

    def _clear_chat_view(self) -> None:
        if hasattr(self.chat, "clear_view"):
            self.chat.clear_view()
        else:
            self.chat.clear()

    def _show_notice(self, text: str) -> None:
        if hasattr(self.chat, "append_system_notice"):
            self.chat.append_system_notice(text)
        elif hasattr(self.chat, "append_line"):
            self.chat.append_line(f"\n[System] {text}\n")
        else:
            self.chat.append(f"<i>{text}</i>")

    def _show_user_message(self, text: str) -> None:
        if hasattr(self.chat, "append_user_message"):
            self.chat.append_user_message(text)
        elif hasattr(self.chat, "append_line"):
            self.chat.append_line(f"\nYou: {text}\n")
        else:
            self.chat.append(f"<b>You:</b> {text}")

    def _show_assistant_message(self, text: str) -> None:
        if hasattr(self.chat, "append_assistant_message"):
            self.chat.append_assistant_message(text)
        elif (
            hasattr(self.chat, "start_assistant_message")
            and hasattr(self.chat, "append_token")
        ):
            self.chat.start_assistant_message()
            self.chat.append_token(text)
            if hasattr(self.chat, "end_assistant_message"):
                self.chat.end_assistant_message()
        elif hasattr(self.chat, "append_line"):
            self.chat.append_line(f"\nAssistant: {text}\n")
        else:
            self.chat.append(f"<b>Assistant:</b> {text}")

    def reload_sessions(self) -> None:
        sessions = self.store.list_sessions()
        self.sidebar.set_sessions(
            [(session.session_id, session.title) for session in sessions]
        )

        if self.active_session_id:
            self.sidebar.select_session(self.active_session_id)

    # ------------------------------------------------------------------
    # Session actions
    # ------------------------------------------------------------------

    def on_new_chat(self) -> None:
        if self.worker and self.worker.isRunning():
            return

        self.active_session_id = None
        self.pending_chat = None
        self.pending_user_message = None
        self.current_assistant_response = ""

        self._clear_chat_view()
        self._show_notice("Ready for a new conversation.")
        self.chat_input.setFocus()

    def on_select_chat(self, session_id: str) -> None:
        if self.worker and self.worker.isRunning():
            return

        self.active_session_id = session_id
        self.pending_chat = None
        self.pending_user_message = None
        self.current_assistant_response = ""

        self._clear_chat_view()
        self._restore_messages(session_id)

    def on_delete_chat(self, session_id: str) -> None:
        if self.worker and self.worker.isRunning():
            return

        self.store.delete(session_id)

        if self.active_session_id == session_id:
            self.active_session_id = None
            self.pending_chat = None
            self.pending_user_message = None
            self._clear_chat_view()
            self._show_notice("Conversation deleted.")

        self.reload_sessions()

    def _restore_messages(self, session_id: str) -> None:
        """Load and display the selected conversation's saved messages."""
        messages = self.store.list_messages(session_id)

        if not messages:
            self._show_notice("This conversation has no saved messages yet.")
            return

        for message in messages:
            if message.role == "user":
                self._show_user_message(message.content)
            elif message.role == "assistant":
                self._show_assistant_message(message.content)
            elif message.role == "system":
                self._show_notice(message.content)

    # ------------------------------------------------------------------
    # Sending messages
    # ------------------------------------------------------------------

    def on_submit_message(self, text: str) -> None:
        text = text.strip()
        if not text:
            return

        if self.worker and self.worker.isRunning():
            return

        self._show_user_message(text)

        if self.active_session_id:
            self.store.add_message(
                session_id=self.active_session_id,
                role="user",
                content=text,
                created_at=self._now_iso(),
            )
        else:
            self.pending_user_message = text
            if self.pending_chat is None:
                self.pending_chat = PendingChat(
                    first_user_text=text,
                    created_at=self._now_iso(),
                )

        payload = {
            "query": text,
            "session_id": self.active_session_id,
            "mode": self._get_selected_mode(),
            "use_rag": self._get_use_rag(),
            "top_k": self._get_top_k(),
        }

        self.current_assistant_response = ""
        self._set_busy(True)

        self.worker = StreamWorker(payload, self)
        self.worker.event_received.connect(self.on_sse_event)
        self.worker.error_occurred.connect(self.on_stream_error)
        self.worker.stream_finished.connect(self.on_stream_finished)
        self.worker.start()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _get_selected_mode(self) -> str:
        mode_widget = getattr(self.topbar, "mode", None)
        if mode_widget is not None and hasattr(mode_widget, "currentText"):
            return mode_widget.currentText()
        return "general_ml"

    def _get_use_rag(self) -> bool:
        rag_widget = getattr(self.topbar, "use_rag", None)
        if rag_widget is not None and hasattr(rag_widget, "isChecked"):
            return bool(rag_widget.isChecked())
        return True

    def _get_top_k(self) -> int:
        top_k_widget = getattr(self.topbar, "top_k", None)
        if top_k_widget is not None and hasattr(top_k_widget, "value"):
            return int(top_k_widget.value())
        return 4

    # ------------------------------------------------------------------
    # SSE event handling
    # ------------------------------------------------------------------

    def on_sse_event(self, event: Dict[str, Any]) -> None:
        event_type = event.get("event")

        if event_type == "start":
            returned_session_id = event.get("session_id")

            if returned_session_id:
                self.active_session_id = str(returned_session_id)
                self._persist_session(self.active_session_id)

                if self.pending_user_message:
                    self.store.add_message(
                        session_id=self.active_session_id,
                        role="user",
                        content=self.pending_user_message,
                        created_at=self._now_iso(),
                    )
                    self.pending_user_message = None

            sources = event.get("sources") or []
            if sources and hasattr(self.chat, "append_sources"):
                self.chat.append_sources(sources)

            self.current_assistant_response = ""

            if hasattr(self.chat, "start_assistant_message"):
                self.chat.start_assistant_message()
            elif hasattr(self.chat, "append_line"):
                self.chat.append_line("\nAssistant: ")

        elif event_type == "chunk":
            token = (
                event.get("content")
                or event.get("token")
                or event.get("delta")
                or event.get("text")
                or ""
            )
            token = str(token)

            if token:
                self.current_assistant_response += token

                if hasattr(self.chat, "append_token"):
                    self.chat.append_token(token)
                elif hasattr(self.chat, "append_line"):
                    self.chat.append_line(token)

        elif event_type == "end":
            if hasattr(self.chat, "end_assistant_message"):
                self.chat.end_assistant_message()
            elif hasattr(self.chat, "append_line"):
                self.chat.append_line("\n")

            self._save_assistant_response()

        elif event_type == "error":
            message = event.get("message") or "Unknown backend error."
            self._show_notice(f"Error: {message}")

    def _save_assistant_response(self) -> None:
        response = self.current_assistant_response.strip()

        if self.active_session_id and response:
            self.store.add_message(
                session_id=self.active_session_id,
                role="assistant",
                content=response,
                created_at=self._now_iso(),
            )

        self.current_assistant_response = ""

    def _persist_session(self, session_id: str) -> None:
        """Create or update the local session record."""
        if self.pending_chat:
            title = self.pending_chat.first_user_text.strip()
            if len(title) > 48:
                title = title[:48].rstrip() + "..."
            created_at = self.pending_chat.created_at
        else:
            existing = self.store.get(session_id)
            if existing:
                title = existing.title
                created_at = existing.created_at
            else:
                title = f"Chat {session_id[-6:]}"
                created_at = self._now_iso()

        self.store.upsert(
            session_id=session_id,
            title=title,
            created_at=created_at,
        )

        self.pending_chat = None
        self.reload_sessions()

    def on_stream_error(self, message: str) -> None:
        self._show_notice(f"Connection error: {message}")

    def on_stream_finished(self) -> None:
        self._set_busy(False)

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(1500)

        event.accept()
