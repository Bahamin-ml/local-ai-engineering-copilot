from __future__ import annotations

from pathlib import Path
from PyQt5.QtWidgets import QApplication

from desktop.ui.main_window import MainWindow


def run_app() -> int:
    app = QApplication([])

    qss_path = Path(__file__).resolve().parent / "resources" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    w = MainWindow()
    w.show()
    return app.exec_()
