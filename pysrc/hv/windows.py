#!/usr/bin/env python

"""
hv Main Window module
"""


import os

from PySide6.QtGui import QStandardItemModel
from PySide6.QtGui import QStandardItem
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QIcon
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QTreeView
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QRadioButton
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QDialogButtonBox

from PySide6 import QtSvg
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject

from hv import utils
from hv import config
from .image import HImage
from .scrollarea import HScrollArea
from .preferences import HPreferences
from .editors import HEditors


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
        config.saveconfig(self.get_configuration())
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
        self.image.defaultbg = self.palette().color(QPalette.Window)
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

    def update_editors(self, editors: list):
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
        for f in utils.getfiles(".", self.masks):
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
        for d in utils.getdirs("."):
            item = QStandardItem(d)
            item.setIcon(i)
            self.dirmodel.setItem(r, 0, item)
            r += 1

        i = QIcon.fromTheme("drive-harddisk")
        for drive in utils.get_drives():
            item = QStandardItem("%{drive}:\\")
            item.setIcon(i)
            self.dirmodel.setItem(r, 0, item)
            r += 1

        self.update_title()

    def dirlist_double_click(self, index):
        item = self.dirmodel.item(index.row()).text()
        self.read_dir(item)

    def filesel_changed(self, new_selection, _):
        ilist = new_selection.indexes()
        if len(ilist) > 0:
            item = self.filemodel.item(ilist[0].row()).text()
            filep = os.path.join(os.getcwd(), item)
#            pixmap = QPixmap(filep)
#            self.image.setPixmap(pixmap)
            self.image.display_file(filep)


    def update_title(self):
        cwd = os.getcwd()
        self.setWindowTitle(f"{cwd} - /hv/")

    def configure(self, startupobj):
        if startupobj:
            self.set_configuration(config.readconfig(), False)
            if os.path.isfile(startupobj):
                dname = os.path.dirname(startupobj)
                self.read_dir(dname)
                self.display_file(startupobj)
            elif os.path.isdir(startupobj):
                self.read_dir(startupobj)
            else:
                self.read_dir()
        else:
            self.set_configuration(config.readconfig(), True)
            self.read_dir()
        self.update_title()

    def get_configuration(self):
        cfg_data = {}
        cfg_data['window'] = {}
        cfg_data['window']['w'] = "%(w)d" % {'w': self.size().width()}
        cfg_data['window']['h'] = "%(h)d" % {'h': self.size().height()}
        cfg_data['window']['x'] = "%(x)d" % {'x': self.pos().x()}
        cfg_data['window']['y'] = "%(y)d" % {'y': self.pos().y()}
        cfg_data['browser'] = {}
        cfg_data['browser']['size-x'] = ",".join(
            [f"{f}" for f in self.hsplitter.sizes()])
        cfg_data['browser']['size-y'] = ",".join(
            [f"{f}" for f in self.vsplitter.sizes()])
        cfg_data['browser']['lastdir'] = os.getcwd()
        cfg_data['settings'] = {}
        cfg_data['settings']['filemasks'] = "|".join(self.masks)
        for elem in ['centered', 'aspect', 'zoom', 'shrink']:
            cfg_data['settings'][elem] = '1' if self.settings[elem] else '0'
        cfg_data['settings']['background'] = "%(b)d" % \
            {'b': self.settings['background']}
        return cfg_data

    def set_configuration(self, configuration: dict, chdir=False):
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
            self.settings['background'] = utils.BACKGROUND_NONE
