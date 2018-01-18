#!/usr/bin/env python

import wx


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
            wx.LC_LIST)
        self.fileList = wx.ListCtrl(
            self.splitterH,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.LC_LIST
        )
        self.splitterH.SplitHorizontally(self.dirList, self.fileList, 250)
        self.imagePanel = wx.Panel(self.splitterV)
        self.splitterV.SplitVertically(self.splitterH, self.imagePanel, 250)
        self.CreateStatusBar()
        self.SetStatusText("/hv/")

    def OnExit(self, event):
        self.Close(True)

    def OnPreferences(self, event):
        hvPrefs = HvPreferences(self)
        hvPrefs.ShowModal()
        hvPrefs.Destroy()


hvApp = wx.App()
hvFrame = HvFrame(None, "/hv/")

hvFrame.Show()
hvApp.MainLoop()
