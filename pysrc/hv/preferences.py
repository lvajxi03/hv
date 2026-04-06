#!/usr/bin/env python3

"""
hv Preferences module
"""


from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QRadioButton
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtCore import Qt

from hv import utils


class HPreferences(QDialog):
    """
    Application preferences dialog
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        gb = QGroupBox("Accepted filemasks")
        v = QVBoxLayout()
        self.usemasks = QCheckBox("Use filemasks:")
        self.masks = QLineEdit()
        v.addWidget(self.usemasks)
        v.addWidget(self.masks)
        gb.setLayout(v)
        vbox.addWidget(gb)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        gb = QGroupBox("Background")
        v = QVBoxLayout()
        self.radio_none = QRadioButton("None")
        self.radio_white = QRadioButton("White")
        self.radio_black = QRadioButton("Black")
        self.radio_checkered = QRadioButton("Checkered")
        self.radio_grid = QRadioButton("Grid")
        v.addWidget(self.radio_none)
        v.addWidget(self.radio_white)
        v.addWidget(self.radio_black)
        v.addWidget(self.radio_checkered)
        v.addWidget(self.radio_grid)
        gb.setLayout(v)
        hbox.addWidget(gb)
        gb = QGroupBox("Settings")
        v = QVBoxLayout()
        self.check_centered = QCheckBox("Centered")
        self.check_aspect = QCheckBox("Aspect")
        self.check_zoom = QCheckBox("Zoom to fit")
        self.check_shrink = QCheckBox("Shrink to fit")
        v.addWidget(self.check_centered)
        v.addWidget(self.check_aspect)
        v.addWidget(self.check_zoom)
        v.addWidget(self.check_shrink)
        gb.setLayout(v)
        hbox.addWidget(gb)
        w = QWidget(self)
        w.setLayout(hbox)
        vbox.addWidget(w)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        vbox.addWidget(frame)
        bbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        vbox.addWidget(bbox)
        self.setLayout(vbox)
        self.setWindowTitle("Preferences")
        self.setContentsMargins(3, 3, 3, 3)
        self.setWindowModality(Qt.ApplicationModal)

    def get_config(self) -> dict:
        """
        Get current configuration controls state
        :return: configuration state
        """
        config = {}
        config['centered'] = self.check_centered.isChecked()
        config['aspect'] = self.check_aspect.isChecked()
        config['zoom'] = self.check_zoom.isChecked()
        config['shrink'] = self.check_shrink.isChecked()
        config['background'] = utils.BACKGROUND_NONE
        btns = {self.radio_none: utils.BACKGROUND_NONE,
                self.radio_white: utils.BACKGROUND_WHITE,
                self.radio_black: utils.BACKGROUND_BLACK,
                self.radio_checkered: utils.BACKGROUND_CHECKERED,
                self.radio_grid: utils.BACKGROUND_GRID}
        for btn in btns:
            if btn.isChecked():
                config['background'] = btns[btn]
        return config

    def set_config(self, configuration: dict):
        self.check_centered.setChecked(configuration['centered'])
        self.check_aspect.setChecked(configuration['aspect'])
        self.check_zoom.setChecked(configuration['zoom'])
        self.check_shrink.setChecked(configuration['shrink'])
        btns = [self.radio_none, self.radio_white, self.radio_black,
                self.radio_checkered, self.radio_grid]
        if 'background' in configuration:
            btns[int(configuration['background'])].setChecked(True)
        else:
            self.radio_none.setChecked(True)
