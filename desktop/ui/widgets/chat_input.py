# desktop/ui/widgets/chat_input.py
from __future__ import annotations

from PyQt5.QtCore import QEvent, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QKeyEvent, QTextDocument
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AutoResizingTextEdit(QTextEdit):
    """
    A multi-line text input that expands automatically based on content
    and sends messages on Enter (Shift+Enter inserts a new line).
    """

    submit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_height = 38
        self.max_height = 160

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptRichText(False)

        # Base font and line metrics
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        self.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #e6edf3;
                selection-background-color: #1f6feb;
                selection-color: #ffffff;
                padding: 4px 6px;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #484f58;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.document().contentsChanged.connect(self._adjust_height)
        self._adjust_height()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.submit_requested.emit()
        else:
            super().keyPressEvent(event)

    def _adjust_height(self) -> None:
        doc: QTextDocument = self.document()
        layout = doc.documentLayout()
        doc_height = int(layout.documentSize().height()) + 8
        new_height = max(self.min_height, min(doc_height, self.max_height))
        self.setFixedHeight(new_height)


class ChatInput(QFrame):
    """
    A ChatGPT-style input container wrapping a multi-line auto-resizing text field,
    action buttons (attachment, voice), and a circular send button.
    """

    message_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_input_container")
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        self.setStyleSheet("""
            QFrame#chat_input_container {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 18px;
            }
            QFrame#chat_input_container:focus-within {
                border: 1px solid #58a6ff;
            }
            QPushButton.composer_action_btn {
                background-color: transparent;
                border: none;
                border-radius: 14px;
                color: #8b949e;
                font-size: 15px;
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
            }
            QPushButton.composer_action_btn:hover {
                background-color: #21262d;
                color: #e6edf3;
            }
            QPushButton#send_button {
                background-color: #e6edf3;
                color: #0d1117;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                font-weight: bold;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
            }
            QPushButton#send_button:hover {
                background-color: #ffffff;
            }
            QPushButton#send_button:disabled {
                background-color: #21262d;
                color: #484f58;
            }
        """)

        # Main layout inside the rounded card
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(14, 10, 14, 10)
        root_layout.setSpacing(6)

        # Multi-line text input
        self.text_edit = AutoResizingTextEdit(self)
        self.text_edit.setPlaceholderText("Ask a question, debug code, or request architecture advice...")
        root_layout.addWidget(self.text_edit)

        # Action bar at bottom of card
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)

        # Attachment button (+)
        self.attach_button = QPushButton("+")
        self.attach_button.setProperty("class", "composer_action_btn")
        self.attach_button.setToolTip("Attach file (Upcoming)")
        self.attach_button.setCursor(Qt.PointingHandCursor)

        # Voice button (Microphone icon)
        self.voice_button = QPushButton("🎙")
        self.voice_button.setProperty("class", "composer_action_btn")
        self.voice_button.setToolTip("Voice input (Upcoming)")
        self.voice_button.setCursor(Qt.PointingHandCursor)

        # Send button (Up arrow circle)
        self.send_button = QPushButton("↑")
        self.send_button.setObjectName("send_button")
        self.send_button.setToolTip("Send message (Enter)")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setEnabled(False)

        actions_layout.addWidget(self.attach_button)
        actions_layout.addWidget(self.voice_button)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.send_button)

        root_layout.addLayout(actions_layout)

    def _connect_signals(self) -> None:
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.submit_requested.connect(self._submit)
        self.send_button.clicked.connect(self._submit)

    def _on_text_changed(self) -> None:
        has_content = bool(self.text_edit.toPlainText().strip())
        self.send_button.setEnabled(has_content)

    def _submit(self) -> None:
        raw_text = self.text_edit.toPlainText().strip()
        if not raw_text or not self.send_button.isEnabled():
            return

        self.message_submitted.emit(raw_text)
        self.text_edit.clear()

    # Public helper methods for MainWindow compatibility
    def text(self) -> str:
        return self.text_edit.toPlainText()

    def clear(self) -> None:
        self.text_edit.clear()

    def setFocus(self) -> None:
        self.text_edit.setFocus()

    def setEnabled(self, enabled: bool) -> None:
        self.text_edit.setEnabled(enabled)
        self.attach_button.setEnabled(enabled)
        self.voice_button.setEnabled(enabled)
        if not enabled:
            self.send_button.setEnabled(False)
        else:
            self._on_text_changed()
