"""
ML Engineering Copilot - Main Window Application
"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QComboBox,
    QCheckBox,
    QTextBrowser,
    QPlainTextEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt
import httpx

from gui.styles import DARK_THEME_QSS, format_message_html
from gui.sidebar import Sidebar
from gui.worker import ChatStreamWorker


class MainWindow(QMainWindow):
    MODE_MAPPING = {
        "General ML": "general_ml",
        "Debug Detective": "debugger",
        "Code Debugger": "debugger",
        "Architecture": "architecture",
        "Model Architect": "architecture",
        "Optimization": "optimization",
        "Pipeline Engineer": "optimization",
        "Concept Explainer": "explainer",
        "Data Analyst": "general_ml"
    }

    def __init__(self, api_base_url: str = "http://127.0.0.1:8000"):
        super().__init__()
        self.api_base_url = api_base_url
        self.current_session_id = None
        self.worker = None

        self.setWindowTitle("ML Engineering Copilot")
        self.resize(1100, 750)
        self.setStyleSheet(DARK_THEME_QSS)

        self._init_ui()
        self._refresh_sessions()
        self._create_new_session()

    def _init_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar
        self.sidebar = Sidebar()
        self.sidebar.session_selected.connect(self._load_session_history)
        self.sidebar.new_chat_requested.connect(self._create_new_session)
        main_layout.addWidget(self.sidebar)

        # 2. Main Chat Panel
        chat_panel = QFrame()
        panel_layout = QVBoxLayout(chat_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        # Header controls
        header = QFrame()
        header.setObjectName("HeaderFrame")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 8, 16, 8)

        lbl_mode = QLabel("Mode:")
        lbl_mode.setStyleSheet("color: #a6adc8; font-weight: bold;")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "general_ml",
            "code_architect",
            "debug_detective",
            "explainer",
            "data_pipeline",
        ])

        self.rag_checkbox = QCheckBox("RAG Augmentation")
        self.rag_checkbox.setChecked(True)

        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet("color: #a6e3a1; font-size: 12px;")

        h_layout.addWidget(lbl_mode)
        h_layout.addWidget(self.mode_combo)
        h_layout.addSpacing(20)
        h_layout.addWidget(self.rag_checkbox)
        h_layout.addStretch()
        h_layout.addWidget(self.status_label)
        panel_layout.addWidget(header)

        # Chat history view
        self.chat_history = QTextBrowser()
        self.chat_history.setObjectName("ChatHistory")
        self.chat_history.setOpenExternalLinks(True)
        panel_layout.addWidget(self.chat_history, stretch=1)

        # Input Area
        input_container = QFrame()
        input_container.setObjectName("InputContainer")
        inp_layout = QHBoxLayout(input_container)
        inp_layout.setContentsMargins(16, 10, 16, 12)
        inp_layout.setSpacing(10)

        self.query_input = QPlainTextEdit()
        self.query_input.setObjectName("QueryInput")
        self.query_input.setPlaceholderText("Ask an ML, PyTorch, or debugging question... (Shift+Enter for new line)")
        self.query_input.setFixedHeight(75)

        self.btn_send = QPushButton("Send")
        self.btn_send.setObjectName("SendBtn")
        self.btn_send.setFixedSize(80, 75)
        self.btn_send.clicked.connect(self._send_message)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setFixedSize(65, 75)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_streaming)

        inp_layout.addWidget(self.query_input)
        inp_layout.addWidget(self.btn_send)
        inp_layout.addWidget(self.btn_stop)
        panel_layout.addWidget(input_container)

        main_layout.addWidget(chat_panel, stretch=1)

    def _refresh_sessions(self):
        try:
            resp = httpx.get(f"{self.api_base_url}/api/sessions", timeout=5.0)
            if resp.status_code == 200:
                sessions = resp.json().get("sessions", [])
                self.sidebar.populate_sessions(sessions, self.current_session_id)
        except Exception:
            pass

    def _create_new_session(self):
        try:
            resp = httpx.post(f"{self.api_base_url}/api/sessions", json={"title": "New ML Chat"}, timeout=5.0)
            if resp.status_code == 201:
                self.current_session_id = resp.json()["session_id"]
                self.chat_history.clear()
                self._append_system_bubble("Started new session. How can I assist with your ML code today?")
                self._refresh_sessions()
        except Exception as e:
            QMessageBox.warning(self, "Connection Error", f"Cannot connect to API server: {e}")

    def _load_session_history(self, session_id: str):
        self.current_session_id = session_id
        self.chat_history.clear()
        try:
            resp = httpx.get(f"{self.api_base_url}/api/sessions/{session_id}", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                for msg in data.get("messages", []):
                    sender = "User" if msg.get("role") == "user" else "Copilot"
                    rag = bool(msg.get("rag_used", False))
                    self._append_bubble(sender, msg.get("content", ""), rag_used=rag)
        except Exception as e:
            self._append_system_bubble(f"Error loading history: {e}")

    def _append_bubble(self, sender: str, text: str, rag_used: bool = False, sources: list = None):
        html_bubble = format_message_html(sender, text, rag_used, sources)
        self.chat_history.append(html_bubble)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def _append_system_bubble(self, text: str):
        self.chat_history.append(f"<div style='color: #6c7086; text-align: center; margin: 8px 0; font-size: 12px;'><i>{text}</i></div>")

    def _send_message(self):
        query = self.query_input.toPlainText().strip()
        if not query:
            return

        self.query_input.clear()
        self._append_bubble("User", query)

        # UI State update
        self.btn_send.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status_label.setText("● Generating...")
        self.status_label.setStyleSheet("color: #fab387; font-size: 12px;")

        # Start background stream worker
        self.worker = ChatStreamWorker(
            base_url=self.api_base_url,
            query=query,
            session_id=self.current_session_id,
            mode=('debugger' if 'debug' in self.mode_combo.currentText().lower() else 'architecture' if 'architect' in self.mode_combo.currentText().lower() else 'optimization' if ('pipe' in self.mode_combo.currentText().lower() or 'optim' in self.mode_combo.currentText().lower()) else 'explainer' if 'explain' in self.mode_combo.currentText().lower() else 'general_ml'),
            use_rag=self.rag_checkbox.isChecked(),
        )

        self._current_assistant_buffer = []
        self._current_rag_meta = {}

        self.worker.stream_started.connect(self._on_stream_start)
        self.worker.token_received.connect(self._on_token_received)
        self.worker.stream_finished.connect(self._on_stream_finished)
        self.worker.error_occurred.connect(self._on_stream_error)
        self.worker.start()

    def _on_stream_start(self, data: dict):
        self._current_rag_meta = data

    def _on_token_received(self, token: str):
        self._current_assistant_buffer.append(token)

    def _on_stream_finished(self, full_answer: str):
        self._cleanup_stream_ui()
        rag_used = self._current_rag_meta.get("rag_used", False)
        sources = self._current_rag_meta.get("sources", [])
        self._append_bubble("Copilot", full_answer, rag_used=rag_used, sources=sources)
        self._refresh_sessions()

    def _on_stream_error(self, err_msg: str):
        self._cleanup_stream_ui()
        self._append_system_bubble(f"⚠️ Error: {err_msg}")

    def _stop_streaming(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(1000)
            self._cleanup_stream_ui()
            self._append_system_bubble("Generation stopped by user.")

    def _cleanup_stream_ui(self):
        self.btn_send.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_label.setText("● Ready")
        self.status_label.setStyleSheet("color: #a6e3a1; font-size: 12px;")
