#!/usr/bin/env python3

"""
hv Editors module
"""


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog


class HEditors(QDialog):
    """
    Application Editors dialog
    """
    def __init__(self, parent=None):
        """
        Create Editors dialog
        :param parent: dialog's parent
        :return: Editor's dialog
        """
        super().__init__(parent)
        self.setWindowTitle("Editors")
        self.resize(640, 480)
        self.setWindowModality(Qt.ApplicationModal)
