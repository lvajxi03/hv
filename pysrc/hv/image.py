#!/usr/bin/env python3

"""
hv Image module
"""


from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel

import hv.res as res
import hv.utils as utils
from .scrollarea import HScrollArea


class HImage(QLabel):
    """
    Main image display class
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.img = None
        self.background = utils.BACKGROUND_NONE
        self.centered = False
        self.shrink = False
        self.zoom = False
        self.aspect = True
        self.checkers = res.load_resource_icon("checkers.xpm")
        self.grid = res.load_resource_icon("grid.xpm")

    def set_centered(self, centered = True):
        self.centered = centered

    def set_shrink(self, shrink = True):
        self.shrink = shrink

    def set_aspect(self, aspect = True):
        self.aspect = aspect

    def set_zoom(self, zoom = True):
        self.zoom = zoom

    def set_background(self, background=utils.BACKGROUND_NONE):
        self.background = background

    def display(self):
        self.clear()
        self.resize(1, 1)
        (w, h) = self.parent.size().width(), self.parent.size().height()
        if self.img:
            pw, ph = self.img.size().width(), self.img.size().height()
            copy = self.img
            shrink = False
            zoom = False

            bigger = utils.is_bigger_than_dp(
                pw, ph, w, h)
            if bigger and self.shrink:
                (pw, ph) = utils.calculate_shrink(
                    pw, ph, w, h, self.aspect)
                shrink = True
            elif not bigger and self.zoom:
                (pw, ph) = utils.calculate_zoom(
                    pw, ph, w, h, self.aspect)
                zoom = True
            (aw, ah) = utils.get_max_rect(
                w, h, pw, ph)
            pi = QPixmap(aw, ah)
            if self.background == utils.BACKGROUND_WHITE:
                pi.fill(Qt.white)
            elif self.background == utils.BACKGROUND_BLACK:
                pi.fill(Qt.black)
            elif self.background == utils.BACKGROUND_GRID:
                pa = QPainter()
                pa.begin(pi)
                pa.drawTiledPixmap(0, 0, aw, ah, QPixmap(self.grid))
                pa.end()
            elif self.background == utils.BACKGROUND_CHECKERED:
                pa = QPainter()
                pa.begin(pi)
                pa.drawTiledPixmap(0, 0, aw, ah, QPixmap(self.checkers))
                pa.end()
            else:
                pi.fill(self.defaultbg)
            if self.centered:
                (x, y) = utils.get_location(aw, ah, pw, ph)
            else:
                x, y = 0, 0
            if zoom or shrink:
                copy = copy.scaled(pw, ph, Qt.IgnoreAspectRatio)
            mask = copy.mask()
            pa = QPainter()
            pa.begin(pi)
#            pa.setOpacity(0.5)
            pa.setBackgroundMode(Qt.TransparentMode)
            pa.drawPixmap(x, y, copy)
            pa.end()
            self.setPixmap(pi)
        else:
            # TODO: image unavailable, do some generic here from utils
            pass

    def display_file(self, filename):
        p = QPixmap(filename)
        self.img = p
        self.origin = p
        self.display()
