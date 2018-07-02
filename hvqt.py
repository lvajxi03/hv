#!/usr/bin/env python

import sys
import os
try:
    from PySide2.QtGui import QStandardItemModel
    from PySide2.QtGui import QStandardItem
    from PySide2.QtGui import QPixmap
    from PySide2.QtGui import QIcon
    from PySide2.QtGui import QPainter
    from PySide2.QtGui import QPalette
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QMainWindow
    from PySide2.QtWidgets import QWidget
    from PySide2.QtWidgets import QHBoxLayout
    from PySide2.QtWidgets import QSplitter
    from PySide2.QtWidgets import QLabel
    from PySide2.QtWidgets import QTreeView
    from PySide2.QtWidgets import QAction
    from PySide2.QtWidgets import QMenu
    from PySide2.QtWidgets import QAbstractItemView
    from PySide2.QtWidgets import QScrollArea
    from PySide2.QtWidgets import QMessageBox
    from PySide2.QtWidgets import QDialog
    from PySide2.QtWidgets import QFrame
    from PySide2.QtWidgets import QVBoxLayout
    from PySide2.QtWidgets import QGroupBox
    from PySide2.QtWidgets import QRadioButton
    from PySide2.QtWidgets import QCheckBox
    from PySide2.QtWidgets import QLineEdit
    from PySide2.QtWidgets import QDialogButtonBox

    from PySide2 import QtSvg
    from PySide2.QtCore import Qt
    from PySide2.QtCore import QObject
except ImportError:
    from PyQt5.QtGui import QStandardItemModel
    from PyQt5.QtGui import QStandardItem
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtGui import QIcon
    from PyQt5.QtGui import QPainter
    from PyQt5.QtGui import QPalette

    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtWidgets import QHBoxLayout
    from PyQt5.QtWidgets import QSplitter
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtWidgets import QTreeView
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtWidgets import QMenu
    from PyQt5.QtWidgets import QAbstractItemView
    from PyQt5.QtWidgets import QScrollArea
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtWidgets import QFrame
    from PyQt5.QtWidgets import QVBoxLayout
    from PyQt5.QtWidgets import QGroupBox
    from PyQt5.QtWidgets import QRadioButton
    from PyQt5.QtWidgets import QCheckBox
    from PyQt5.QtWidgets import QLineEdit
    from PyQt5.QtWidgets import QDialogButtonBox
    from PyQt5 import QtSvg
    from PyQt5.QtCore import Qt
    from PyQt5.QtCore import QObject
import hvcommon

class HScrollArea(QScrollArea):

    def resizeEvent(self, new_size):
        if self.image:
            self.image.display()

    def set_image(self, image=None):
        self.image = image

class HImage(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.img = None
        self.background = hvcommon.BACKGROUND_NONE
        self.centered = False
        self.shrink = False
        self.zoom = False
        self.aspect = True

    def set_centered(self, centered = True):
        self.centered = centered

    def set_shrink(self, shrink = True):
        self.shrink = shrink

    def set_aspect(self, aspect = True):
        self.aspect = aspect

    def set_zoom(self, zoom = True):
        self.zoom = zoom

    def set_background(self, background=hvcommon.BACKGROUND_NONE):
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

            bigger = hvcommon.is_bigger_than_dp(
                pw, ph, w, h)
            if bigger and self.shrink:
                (pw, ph) = hvcommon.calculate_shrink(
                    pw, ph, w, h, self.aspect)
                shrink = True
            elif not bigger and self.zoom:
                (pw, ph) = hvcommon.calculate_zoom(
                    pw, ph, w, h, self.aspect)
                zoom = True
            (aw, ah) = hvcommon.get_max_rect(
                w, h, pw, ph)
            pi = QPixmap(aw, ah)
            if self.background == hvcommon.BACKGROUND_WHITE:
                pi.fill(Qt.white)
            elif self.background == hvcommon.BACKGROUND_BLACK:
                pi.fill(Qt.black)
            elif self.background == hvcommon.BACKGROUND_GRID:
                c = QPixmap(hvcommon.grid)
                pa = QPainter()
                pa.begin(pi)
                pa.drawTiledPixmap(0, 0, aw, ah, c)
                pa.end()
            elif self.background == hvcommon.BACKGROUND_CHECKERED:
                c = QPixmap(hvcommon.checkers)
                pa = QPainter()
                pa.begin(pi)
                pa.drawTiledPixmap(0, 0, aw, ah, c)
                pa.end()
            else:
                pi.fill(self.defaultbg)
            if self.centered:
                (x, y) = hvcommon.get_location(aw, ah, pw, ph)
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
            # TODO: image unavailable, do some generic here from hvcommon
            pass

    def display_file(self, filename):
        p = QPixmap(filename)
        self.img = p
        self.origin = p
        self.display()

class HPreferences(QDialog):

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

    def get_config(self):
        config = {}
        config['centered'] = self.check_centered.isChecked()
        config['aspect'] = self.check_aspect.isChecked()
        config['zoom'] = self.check_zoom.isChecked()
        config['shrink'] = self.check_shrink.isChecked()
        config['background'] = hvcommon.BACKGROUND_NONE
        btns = {self.radio_none: hvcommon.BACKGROUND_NONE,
                self.radio_white: hvcommon.BACKGROUND_WHITE,
                self.radio_black: hvcommon.BACKGROUND_BLACK,
                self.radio_checkered: hvcommon.BACKGROUND_CHECKERED,
                self.radio_grid: hvcommon.BACKGROUND_GRID}
        for btn in btns:
            if btn.isChecked():
                config['background'] = btns[btn]
        return config

    def set_config(self, config={}):
        self.check_centered.setChecked(config['centered'])
        self.check_aspect.setChecked(config['aspect'])
        self.check_zoom.setChecked(config['zoom'])
        self.check_shrink.setChecked(config['shrink'])
        btns = [self.radio_none, self.radio_white, self.radio_black,
                self.radio_checkered, self.radio_grid]
        if 'background' in config:
            btns[int(config['background'])].setChecked(True)
        else:
            self.radio_none.setChecked(True)

class HEditors(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editors")
        self.resize(640, 480)
        self.setWindowModality(Qt.ApplicationModal)


class HWindow(QMainWindow):
    def __init__(self, startupobj):
        super().__init__()
        self.image = None
        self.current = None
        self.create_ui()
        self.settings = {}
        self.masks = []
        self.configure(startupobj)

    def closeEvent(self, event):
        hvcommon.saveconfig(self.get_configuration())
        event.accept()

    def create_ui(self):
        self.image_menu = QMenu(self)
        item = QAction("Flip &horizontally", self.image_menu)
        self.image_menu.addAction(item)
        item = QAction("Flip &vertically", self.image_menu)
        self.image_menu.addAction(item)
        item = QAction("Rotate &clockwise", self.image_menu)
        self.image_menu.addAction(item)
        item = QAction("Rotate c&ounter clockwise", self.image_menu)
        self.image_menu.addAction(item)
        self.editors_menu = self.image_menu.addMenu("&Edit in...")

        w = QWidget()
        self.dirmodel = QStandardItemModel(0, 3, w)
        self.filemodel = QStandardItemModel(0, 3, w)

        hbox = QHBoxLayout(w)
        self.hsplitter = QSplitter(Qt.Horizontal)
        self.vsplitter = QSplitter(Qt.Vertical)

        self.dirlist = QTreeView()
        self.dirlist.setModel(self.dirmodel)
        self.dirlist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dirlist.setRootIsDecorated(False)
        self.dirlist.setAlternatingRowColors(True)
        self.dirlist.doubleClicked.connect(
            self.dirlist_double_click)

        self.filelist = QTreeView()
        self.filelist.setModel(self.filemodel)
        self.filelist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filelist.setRootIsDecorated(False)
        self.filelist.setAlternatingRowColors(True)
        self.filelist.selectionModel().selectionChanged.connect(
            self.filesel_changed)

        self.vsplitter.addWidget(self.dirlist)
        self.vsplitter.addWidget(self.filelist)

        self.scroll = HScrollArea()
        self.image = HImage(self.scroll)
        self.image.defaultbg = self.palette().color(QPalette.Background)
        self.image.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image.customContextMenuRequested.connect(self.popup_image_menu)
        self.image.setAlignment(Qt.AlignCenter)
        self.scroll.set_image(self.image)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.image)
        self.hsplitter.addWidget(self.vsplitter)
        self.hsplitter.addWidget(self.scroll)
        hbox.addWidget(self.hsplitter)
        hbox.setContentsMargins(0, 0, 0, 0)
        w.setLayout(hbox)
        self.update_statusbar()
        self.setCentralWidget(w)

        menubar = self.menuBar()
        menu = menubar.addMenu("h&v")
        item = QAction("About", self)
        item.triggered.connect(self.on_about)
        menu.addAction(item)
        menu = menubar.addMenu("&File")
        item = QAction("&Preferences", self)
        item.triggered.connect(self.on_preferences)
        menu.addAction(item)
        item = QAction("&Editors", self)
        item.triggered.connect(self.on_editors)
        menu.addAction(item)
        menu.addSeparator()
        item = QAction("&Quit", self)
        item.triggered.connect(self.close)
        menu.addAction(item)

        self.hsplitter.setSizes([300, 900])
        self.vsplitter.setSizes([300, 900])

    def popup_image_menu(self, point):
        self.image_menu.exec_(self.image.mapToGlobal(point))

    def on_editors(self):
        ed = HEditors(self)
        response = ed.exec_()
        if response == 1:
            pass

    def on_preferences(self):
        pd = HPreferences(self)
        pd.set_config(self.settings)
        response = pd.exec_()
        if response == 1:
            self.settings = pd.get_config()
            self.image.set_centered(self.settings['centered'])
            self.image.set_zoom(self.settings['zoom'])
            self.image.set_aspect(self.settings['aspect'])
            self.image.set_shrink(self.settings['shrink'])
            self.image.set_background(self.settings['background'])
            self.image.display()

    def on_about(self):
        ad = QMessageBox()
        ad.setIcon(QMessageBox.Information)
        ad.setText("hv\nPyQt/PySide image viewer\n(C) Marcin Bielewicz 2017-?")
        ad.setInformativeText("More on github")
        ad.setWindowTitle("About hv")
        ad.setDetailedText("Detailed text")
        ad.setStandardButtons(QMessageBox.Ok)
        ad.exec_()

    def on_editor_caller(self, item):
        return lambda: self.on_editor(item)

    def on_editor(self, item):
        (label, command) = self.editor_commands[item]

    def update_editors(self, editors=[]):
        self.editors_menu.clear()
        self.editor_commands = {}
        for editor in editors:
            (label, command) = editor
            item = QAction(label, self.editors_menu)
            item.triggered.connect(self.on_editor_caller(item))
            self.editor_commands[item] = (label, command)
            self.editors_menu.addAction(item)

    def update_statusbar(self, fname=None, ftype=None):
        msg = '/hv/'
        if self.current:
            msg = 'File: %(n)s, type: %(t)s - /hv/' % \
                {'n': fname, 't': ftype}
        self.statusBar().showMessage(msg)

    def read_dir(self, dirname="."):

        # Clear data at first:
        dc = self.dirmodel.rowCount()
        fc = self.filemodel.rowCount()
        self.dirmodel.removeRows(0, dc)
        self.filemodel.removeRows(0, fc)

        # Set headers data again: apparently they are cleared
        # on every model clean
        self.dirmodel.setHeaderData(0, Qt.Horizontal, "Dirname")
        self.dirmodel.setHeaderData(1, Qt.Horizontal, "Last modified")
        self.dirmodel.setHeaderData(2, Qt.Horizontal, "Size")

        self.filemodel.setHeaderData(0, Qt.Horizontal, "Filename")
        self.filemodel.setHeaderData(1, Qt.Horizontal, "Size")
        self.filemodel.setHeaderData(2, Qt.Horizontal, "Last modified")

        if not dirname:
            dirname = "."
        os.chdir(dirname)

        r = 0
        fi = QIcon.fromTheme("image-x-generic", QIcon(":/image-x-generic.png"))
        for f in hvcommon.getfiles(".", self.masks):
            item = QStandardItem(f[0])
            item.setIcon(fi)
            self.filemodel.setItem(r, 0, item)
            item = QStandardItem(f[1])
            self.filemodel.setItem(r, 2, item)
            item = QStandardItem(f[2])
            self.filemodel.setItem(r, 1, item)
            r += 1

        r = 0
        item = QStandardItem(".")
        i = QIcon.fromTheme("view-refresh")
        item.setIcon(i)
        self.dirmodel.setItem(r, 0, item)

        r += 1
        item = QStandardItem("..")
        i = QIcon.fromTheme("go-up")
        item.setIcon(i)
        self.dirmodel.setItem(r, 0, item)
        r += 1

        i = QIcon.fromTheme("folder-pictures")
        for d in hvcommon.getdirs("."):
            item = QStandardItem(d)
            item.setIcon(i)
            self.dirmodel.setItem(r, 0, item)
            r += 1

        i = QIcon.fromTheme("drive-harddisk")
        for drive in hvcommon.get_drives():
            item = QStandardItem("%(letter)s:\\" % {'letter': drive})
            item.setIcon(i)
            self.dirmodel.setItem(r, 0, item)
            r += 1

        self.update_title()

    def dirlist_double_click(self, index):
        item = self.dirmodel.item(index.row()).text()
        self.read_dir(item)

    def filesel_changed(self, new_selection, old_selection):
        ilist = new_selection.indexes()
        if len(ilist) > 0:
            item = self.filemodel.item(ilist[0].row()).text()
            filep = os.path.join(os.getcwd(), item)
#            pixmap = QPixmap(filep)
#            self.image.setPixmap(pixmap)
            self.image.display_file(filep)


    def update_title(self):
        self.setWindowTitle("%(d)s - /hv/" % {'d': os.getcwd()})

    def configure(self, startupobj):
        if startupobj:
            self.set_configuration(hvcommon.readconfig(), False)
            if os.path.isfile(startupobj):
                dname = os.path.dirname(startupobj)
                self.read_dir(dname)
                self.display_file(startupobj)
            elif os.path.isdir(startupobj):
                self.read_dir(startupobj)
            else:
                self.read_dir()
        else:
            self.set_configuration(hvcommon.readconfig(), True)
            self.read_dir()
        self.update_title()

    def get_configuration(self):
        config = {}
        config['window'] = {}
        config['window']['w'] = "%(w)d" % {'w': self.size().width()}
        config['window']['h'] = "%(h)d" % {'h': self.size().height()}
        config['window']['x'] = "%(x)d" % {'x': self.pos().x()}
        config['window']['y'] = "%(y)d" % {'y': self.pos().y()}
        config['browser'] = {}
        config['browser']['size-x'] = ",".join(["%(n)d" % {'n': f} for f in self.hsplitter.sizes()])        
        config['browser']['size-y'] = ",".join(["%(n)d" % {'n': f} for f in self.vsplitter.sizes()])
        config['browser']['lastdir'] = os.getcwd()
        config['settings'] = {}
        config['settings']['filemasks'] = "|".join(self.masks)
        for elem in ['centered', 'aspect', 'zoom', 'shrink']:            
            config['settings'][elem] = '1' if self.settings[elem] else '0'
        config['settings']['background'] = "%(b)d" % \
            {'b': self.settings['background']}
        return config

    def set_configuration(self, configuration={}, chdir=False):
        try:
            x = int(configuration['window']['x'])
            y = int(configuration['window']['y'])
            self.move(x, y)
        except KeyError:
            pass
        try:
            w = int(configuration['window']['w'])
            h = int(configuration['window']['h'])
            self.resize(w, h)
        except KeyError:
            pass
        try:
            ld = configuration['browser']['lastdir']
            if chdir and ld:
                os.chdir(ld)
        except KeyError:
            pass
        except IOError:
            pass
        except OSError:
            pass
        try:
            sizex = configuration['browser']['size-x']
            sizes = [int(a.strip()) for a in sizex.split(",")]
            self.hsplitter.setSizes(sizes)
        except KeyError:
            pass
        try:
            sizex = configuration['browser']['size-y']
            sizes = [int(a.strip()) for a in sizex.split(",")]
            self.vsplitter.setSizes(sizes)
        except KeyError:
            pass        
        try:
            self.settings = configuration['settings']
        except KeyError:
            pass
        if 'filemasks' in self.settings:
            masks = self.settings['filemasks'].split("|")
            self.masks = [f for f in masks if f]
        if 'editors' in configuration:
            self.editors = configuration['editors']
        self.update_editors(self.editors)
        if 'centered' in self.settings:
            self.image.set_centered(self.settings['centered'])
        else:
            self.settings['centered'] = False
        if 'zoom' in self.settings:
            self.image.set_zoom(self.settings['zoom'])
        else:
            self.settings['zoom'] = False
        if 'aspect' in self.settings:
            self.image.set_aspect(self.settings['aspect'])
        else:
            self.settings['aspect'] = True
        if 'shrink' in self.settings:
            self.image.set_shrink(self.settings['shrink'])
        else:
            self.settings['shrink'] = False
        if 'background' in self.settings:
            self.settings['background'] = int(self.settings['background'])
            self.image.set_background(self.settings['background'])
        else:
            self.settings['background'] = hvcommon.BACKGROUND_NONE

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        so = sys.argv[1]
    except IndexError:
        so = None
    window = HWindow(so)
    window.show()
    sys.exit(app.exec_())
