#!/usr/bin/env python3

"""
Package startup
"""


import sys
from PySide6.QtWidgets import QApplication
from .windows import HWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        so = sys.argv[1]
    except IndexError:
        so = None
    window = HWindow(so)
    window.show()
    sys.exit(app.exec())
