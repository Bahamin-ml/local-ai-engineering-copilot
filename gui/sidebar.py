"""
Sidebar widget for Session listing and creation.
"""

from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import pyqtSignal


class Sidebar(QFrame):
    session_selected = pyqtSignal(str)
    new_chat_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarFrame")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(10)

        # Title
        self.app_title = QLabel("ML Copilot")
        self.app_title.setObjectName("AppTitle")
        layout.addWidget(self.app_title)

        # New Chat Button
        self.btn_new = QPushButton("+ New Chat")
        self.btn_new.setObjectName("NewChatBtn")
        self.btn_new.clicked.connect(self.new_chat_requested.emit)
        layout.addWidget(self.btn_new)

        # Sessions list
        self.lbl_history = QLabel("Conversations")
        self.lbl_history.setStyleSheet("color: #6c7086; font-size: 11px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(self.lbl_history)

        self.session_list = QListWidget()
        self.session_list.setObjectName("SessionList")
        self.session_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.session_list)

    def populate_sessions(self, sessions: list, current_session_id: str = None):
        self.session_list.clear()
        for s in sessions:
            sess_id = s.get("session_id") or s.get("id")
            title = s.get("title") or "ML Chat"
            item = QListWidgetItem(title)
            item.setData(1000, sess_id)
            self.session_list.addItem(item)
            if current_session_id and sess_id == current_session_id:
                self.session_list.setCurrentItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        sess_id = item.data(1000)
        if sess_id:
            self.session_selected.emit(sess_id)
