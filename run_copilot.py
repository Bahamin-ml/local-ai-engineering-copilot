"""
ML Engineering Copilot - Desktop Application Launcher
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ML Engineering Copilot")

    window = MainWindow(api_base_url="http://127.0.0.1:8000")
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
