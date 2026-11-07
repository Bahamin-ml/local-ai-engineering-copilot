from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox


class SessionSidebar(QWidget):
    new_requested = pyqtSignal()
    delete_requested = pyqtSignal(str)
    selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.title = QLabel("Chats")
        self.list = QListWidget()

        self.new_btn = QPushButton("New")
        self.delete_btn = QPushButton("Delete")

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.new_btn, 1)
        btn_row.addWidget(self.delete_btn, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.list, 1)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        self.new_btn.clicked.connect(self.new_requested.emit)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.list.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        it = self.list.currentItem()
        if not it:
            return
        session_id = it.data(256)  # Qt.UserRole
        if session_id:
            self.selected.emit(session_id)

    def _on_delete_clicked(self):
        it = self.list.currentItem()
        if not it:
            return
        session_id = it.data(256)
        if not session_id:
            return

        ok = QMessageBox.question(
            self,
            "Delete chat",
            "Delete selected chat from desktop list? (Server memory will remain unless backend supports deletion.)",
        )
        if ok == QMessageBox.Yes:
            self.delete_requested.emit(session_id)

    def set_sessions(self, items: list[tuple[str, str]]):
        """
        items: [(session_id, title)]
        """
        self.list.clear()
        for session_id, title in items:
            from PyQt5.QtWidgets import QListWidgetItem

            it = QListWidgetItem(title)
            it.setData(256, session_id)
            self.list.addItem(it)

    def select_session(self, session_id: str):
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.data(256) == session_id:
                self.list.setCurrentItem(it)
                return
