#!/usr/bin/env python

import wx


class HvFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(wx.Frame, self).__init__(*args, **kw)
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

    def OnExit(self, event):
        self.Close(True)

    def OnPreferences(self, event):
        pass


hvApp = wx.App()
hvFrame = HvFrame(None, title="/hv/")

hvFrame.Show()
hvApp.MainLoop()
