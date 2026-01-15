import sys
from PyQt6.QtWidgets import QApplication
from src.tracker import InputTracker
from src.ui import OverlayWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tracker = InputTracker()
    window = OverlayWidget(tracker)
    window.show()
    sys.exit(app.exec())
