from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QCheckBox, QSpinBox


class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.mode = QComboBox()
        self.mode.addItems(["general_ml", "debugger", "architecture", "optimization", "explainer"])

        self.use_rag = QCheckBox("Use RAG")
        self.use_rag.setChecked(True)

        self.top_k = QSpinBox()
        self.top_k.setRange(1, 20)
        self.top_k.setValue(4)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.mode)
        layout.addSpacing(12)
        layout.addWidget(self.use_rag)
        layout.addSpacing(12)
        layout.addWidget(QLabel("top_k:"))
        layout.addWidget(self.top_k)
        layout.addStretch(1)
        self.setLayout(layout)
