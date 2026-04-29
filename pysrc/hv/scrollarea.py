#!/usr/bin/env python3

"""
hv ScrollArea module
"""


from PySide6.QtWidgets import QScrollArea


class HScrollArea(QScrollArea):
    """
    Image display scroll area class
    """
    def resizeEvent(self, new_size):
        """
        Handle new size event
        :param new_size: new scroll area size"
        """
        if self.image:
            self.image.display()

    def set_image(self, image=None):
        """
        Set new image
        :param image: new image
        """
        self.image = image
