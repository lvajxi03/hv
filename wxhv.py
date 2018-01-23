#!/usr/bin/env python

import wx
import os
import fnmatch
import ConfigParser
import datetime

have_windows = False

try:
    import string
    from ctypes import windll
    have_windows = True
except ImportError:
    pass


def get_drives():
    drives = []
    if have_windows:
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1
    return drives


def getfiles(curdir=".", masks=[]):
    try:
        names = []
        os.chdir(curdir)
        if len(masks) > 0:
            for f in os.listdir(curdir):
                if os.path.isfile(f):
                    for mask in masks:
                        if fnmatch.fnmatch(f, mask):
                            names.append(f)
        else:
            for f in os.listdir(curdir):
                if os.path.isfile(f):
                    names.append(f)
        names.sort()

        full = []
        for name in names:
            mtime = os.path.getmtime(name)
            ts = datetime.datetime.fromtimestamp(
                mtime).strftime('%Y-%m-%d %H:%M:%S')
            statinfo = os.stat(name)
            size = statinfo.st_size
            full.append([name, ts, size])

        return full
    except OSError:
        pass
    return []


def getdirs(curdir="."):
    try:
        os.chdir(curdir)
        dirs = []
        for f in os.listdir(curdir):
            if os.path.isdir(f):
                dirs.append(f)
        dirs.sort()
        return dirs
    except OSError:
        pass
    return []


def saveconfig(configuration={}):
    fh = open(os.path.join(os.path.expanduser("~"), ".hvrc"), "w")
    cp = ConfigParser.ConfigParser()
    for key in configuration:
        cp.add_section(key)
        for subkey in configuration[key]:
            cp.set(key, subkey, configuration[key][subkey])
    cp.write(fh)
    fh.close()


def readconfig():
    configuration = {}
    try:
        fh = open(os.path.join(os.path.expanduser("~"), ".hvrc"))
        cp = ConfigParser.ConfigParser()
        cp.readfp(fh)
        for section in cp.sections():
            configuration[section] = {}
            for tuple in cp.items(section):
                configuration[section][tuple[0]] = tuple[1]
        fh.close()
    except IOError:
        pass
    # Saturday night specials:
    if 'settings' in configuration:
        for key in ['centered', 'aspect', 'maximize', 'shrink']:
            try:
                if configuration['settings'][key] == 'True':
                    configuration['settings'][key] = True
                else:
                    configuration['settings'][key] = False
            except KeyError:
                configuration['settings'][key] = False
    return configuration


class HvPreferences(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            title="Preferences",
        )

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        panel = wx.Panel(self, 1)
        sb = wx.StaticBox(panel, label='Accepted file masks')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        self.masks = wx.CheckBox(
            panel,
            label='Accept following file masks:')
        sbs.Add(self.masks, 0, wx.EXPAND | wx.ALL, 5)
        self.entry = wx.TextCtrl(panel)
        sbs.Add(self.entry, 0, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sbs)
        vbox.Add(panel, 1, wx.EXPAND)

        panel = wx.Panel(self, 1)
        sb = wx.StaticBox(panel, label='Background')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        self.bg_none = wx.RadioButton(
            panel,
            label='None',
            style=wx.RB_GROUP)
        sbs.Add(self.bg_none)
        self.bg_white = wx.RadioButton(
            panel,
            label='White',
            style=wx.RB_GROUP)
        sbs.Add(self.bg_white)
        self.bg_black = wx.RadioButton(
            panel,
            label='Black',
            style=wx.RB_GROUP)
        sbs.Add(self.bg_black)
        self.bg_checkered = wx.RadioButton(
            panel,
            label='Checkered',
            style=wx.RB_GROUP)
        sbs.Add(self.bg_checkered)

        panel.SetSizer(sbs)

        hbox.Add(panel, 1, wx.EXPAND)
        panel = wx.Panel(self, 1)
        sb = wx.StaticBox(panel, label='Settings')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        self.se_centered = wx.CheckBox(
            panel,
            label="Centered")
        sbs.Add(self.se_centered, border=5)

        self.se_aspect = wx.CheckBox(
            panel,
            label="Keep aspect ratio")
        sbs.Add(self.se_aspect)

        self.se_zoom = wx.CheckBox(
            panel,
            label='Zoom to fit')
        sbs.Add(self.se_zoom)

        self.se_shrink = wx.CheckBox(
            panel,
            label='Shrink to fit')
        sbs.Add(self.se_shrink)

        panel.SetSizer(sbs)

        hbox.Add(panel, 1, wx.EXPAND)
        vbox.Add(hbox, 1, wx.EXPAND)

        sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(sizer, 0, wx.EXPAND)

        self.SetSizer(vbox)
        self.Fit()

    def OnAccept(self, event):
        self.Destroy()

    def OnClose(self, event):
        self.Destroy()


class HvFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(
            self,
            parent,
            title=title,
            size=(800, 600))
        self.masks = []
        self.create_ui()

    def create_ui(self):
        submenu = wx.Menu()
        subitem = submenu.Append(
            -1,
            "&Preferences\tCtrl-P",
            "Show preferences dialog")
        self.Bind(wx.EVT_MENU, self.OnPreferences, subitem)
        subitem = submenu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnExit, subitem)
        bar = wx.MenuBar()
        bar.Append(submenu, "&hv")
        self.SetMenuBar(bar)

        self.splitterV = wx.SplitterWindow(
            self,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_THIN_SASH,
            "hv-vertical-split-window"
        )
        self.splitterH = wx.SplitterWindow(
            self.splitterV,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.SP_THIN_SASH,
            "hv-horizontal-split-window"
        )
        self.dirList = wx.ListCtrl(
            self.splitterH,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.LC_REPORT | wx.LC_NO_HEADER)
        self.dirList.InsertColumn(0, 'Directory name')
        self.dirList.InsertColumn(1, 'Date')
        self.dirList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDblClickDirList)
        self.fileList = wx.ListCtrl(
            self.splitterH,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.LC_REPORT | wx.LC_VRULES)
        self.fileList.InsertColumn(0, 'Filename')
        self.fileList.InsertColumn(1, 'Size')
        self.fileList.InsertColumn(2, 'Date')
        self.fileList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectFileList)
        self.splitterH.SplitHorizontally(self.dirList, self.fileList, 250)
        self.imagePanel = wx.Panel(self.splitterV)
        self.splitterV.SplitVertically(self.splitterH, self.imagePanel, 250)
        self.CreateStatusBar()
        self.SetStatusText("/hv/")

    def OnSelectFileList(self, event):
        item = event.GetItem()
        text = item.GetText()

    def OnDblClickDirList(self, event):
        dname = event.GetItem().GetText()
        if not dname:
            dname = "."
        self.read_dir(dname)

    def OnExit(self, event):
        self.Close(True)

    def OnPreferences(self, event):
        hvPrefs = HvPreferences(self)
        hvPrefs.ShowModal()
        hvPrefs.Destroy()

    def read_dir(self, dirname="."):
        if not dirname:
            dirname = "."
        os.chdir(dirname)

        self.fileList.DeleteAllItems()
        self.dirList.DeleteAllItems()

        itemNo = 0
        for f in getfiles(".", self.masks):
            self.fileList.InsertStringItem(itemNo, f[0])
            self.fileList.SetItem(itemNo, 1, "%(x)d" % {'x': f[2]})
            self.fileList.SetItem(itemNo, 2, f[1])
            itemNo += 1

        self.dirList.InsertStringItem(0, '.')
        self.dirList.InsertStringItem(0, '..')
        itemNo = 2
        for d in getdirs():
            self.dirList.InsertStringItem(itemNo, d)
            itemNo += 1

        for drive in get_drives():
            self.dirList.InsertStringItem(
                itemNo,
                "%(letter)s:\\"
                % {'letter': drive})
            itemNo += 1
        self.SetTitle(
            "%(d)s - /hv/"
            % {
                'd': os.getcwd()})


hvApp = wx.App()
hvFrame = HvFrame(None, "/hv/")
hvFrame.read_dir()

hvFrame.Show()
hvApp.MainLoop()
