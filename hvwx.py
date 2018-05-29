#!/usr/bin/env python

import wx
import os
import hvcommon


class HvImage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(
            self,
            parent,
            style=wx.SUNKEN_BORDER)
        self.Bind(wx.EVT_PAINT, self.OnPaintEvent)
        self.image = None
        self.background = hvcommon.BACKGROUND_CHECKERED
        self.centered = True
        self.shrink = False
        self.zoom = False

    def loadImage(self, filename):
        self.image = wx.Image()
        if self.image.CanRead(filename):
            self.image.LoadFile(filename)
        else:
            self.image = None
        self.paint()

    def render(self, dc):
        if self.image:
            imageSize = self.image.GetSize()
            panelSize = self.GetSize()
            if self.background == hvcommon.BACKGROUND_NONE:
                dc.Clear()
            elif self.background == hvcommon.BACKGROUND_WHITE:
                dc.Clear()
                dc.FloodFill(0, 0, wx.Colour(255, 255, 255), wx.FLOOD_SURFACE)
            elif self.background == hvcommon.BACKGROUND_BLACK:
                dc.Clear()
                dc.FloodFill(1, 1, wx.Colour(0, 0, 0), wx.FLOOD_SURFACE)
            elif self.background == hvcommon.BACKGROUND_CHECKERED:
                dc.Clear()  # Temporary, until better solution found
                # chkbmp = wx.BitmapFromXPMData(hvcommon.checkers)
                # tx = panelSize.width / 100
                # ty = panelSize.height / 100
                # if panelSize.width % 100 > 0:
                #     tx = tx + 1
                # if panelSize.height % 100 > 0:
                #     ty = ty + 1
                # for i in range(0, tx):
                #     for j in range(0, ty):
                #         dc.DrawBitmap(
                #             chkbmp,
                #             i * 100,
                #             j * 100,
                #             False)
                pass
            if self.centered:
                (x, y) = hvcommon.get_location(
                    panelSize.width,
                    panelSize.height,
                    imageSize.width,
                    imageSize.height)
            else:
                x = 0
                y = 0
            dc.DrawBitmap(wx.Bitmap(self.image), x, y, False)
        else:
            dc.Clear()

    def paint(self):
        dc = wx.ClientDC(self)
        self.render(dc)

    def OnPaintEvent(self, event):
        dc = wx.ClientDC(self)
        self.render(dc)


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
        bar.Append(submenu, "h&v")
        submenu = wx.Menu()
        subitem = submenu.Append(
            -1,
            "&About",
            "About hv")
        self.Bind(wx.EVT_MENU, self.OnAbout, subitem)
        bar.Append(submenu, "&Help")
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
        self.imagePanel = HvImage(self.splitterV)
        self.splitterV.SplitVertically(self.splitterH, self.imagePanel, 250)
        self.CreateStatusBar()
        self.SetStatusText("/hv/")

    def OnSelectFileList(self, event):
        item = event.GetItem()
        text = item.GetText()
        self.imagePanel.loadImage(text)

    def OnDblClickDirList(self, event):
        dname = event.GetItem().GetText()
        if not dname:
            dname = "."
        self.read_dir(dname)

    def OnExit(self, event):
        self.Close(True)

    def OnAbout(self, event):
        ab = wx.MessageDialog(
            self,
            "hv\nwxPython image viewer\n(C) Marcin Bielewicz, 2017-?",
            "About hv",
            wx.OK | wx.ICON_INFORMATION)
        ab.ShowModal()
        ab.Destroy()

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
        for f in hvcommon.getfiles(".", self.masks):
            self.fileList.InsertStringItem(itemNo, f[0])
            self.fileList.SetItem(itemNo, 1, f[2])
            self.fileList.SetItem(itemNo, 2, f[1])
            itemNo += 1

        self.dirList.InsertStringItem(0, '.')
        self.dirList.InsertStringItem(0, '..')
        itemNo = 2
        for d in hvcommon.getdirs():
            self.dirList.InsertStringItem(itemNo, d)
            itemNo += 1

        for drive in hvcommon.get_drives():
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
