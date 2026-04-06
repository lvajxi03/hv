#!/usr/bin/env python

"""
hv Resources module
"""


from importlib import resources
from PySide6.QtGui import QPixmap


def load_resource_icon(filename) -> QPixmap:
    """
    Load an icon from resources
    """
    # 'moj_projekt.icons' to ścieżka kropkowa do folderu z ikonami
    traversable = resources.files('hv.assets').joinpath(filename)

    # Context manager `as_file` provides a file existing on disk
    # (even if it shall be expanded from .whl file):
    with resources.as_file(traversable) as path:
        return QPixmap(str(path))
