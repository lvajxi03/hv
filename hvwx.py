#!/usr/bin/env python

import wx
import os
import sys
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

    def display_file(self, filename):
        self.image = wx.Image()
        if self.image.CanRead(filename):
            self.image.LoadFile(filename)
        else:
            self.image = None
        self.display()

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

    def display(self):
        dc = wx.ClientDC(self)
        self.render(dc)

    def OnPaintEvent(self, event):
        dc = wx.ClientDC(self)
        self.render(dc)


class HEditors(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self,
            parent,
            title="Editors",
        )

        self.labels = []
        self.commands = []
        self.bindings = {}
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self, 1)
        sb = wx.StaticBox(panel, label='Available editors')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        panel2 = wx.Panel(panel, 1)
        sbs.Add(panel2, 0, wx.EXPAND | wx.ALL, 1)
        gs = wx.GridSizer(5)
        for i in range(10):
            l = wx.StaticText(panel2, label="label: ")
            gs.Add(l)
            t = wx.TextCtrl(panel2)
            self.labels.append(t)
            gs.Add(t)
            l = wx.StaticText(panel2, label="command: ")
            gs.Add(l)
            c = wx.TextCtrl(panel2)
            self.commands.append(c)
            gs.Add(c)
            b = wx.Button(panel2, label="...")
            b.Bind(wx.EVT_BUTTON, self.OnBrowse)
            self.bindings[b] = c
            gs.Add(b)
        panel2.SetSizer(gs)
        panel.SetSizer(sbs)
        vbox.Add(panel, 1, wx.EXPAND)
        s = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        vbox.Add(s, 0, wx.EXPAND)
        self.SetSizer(vbox)
        self.Fit()

    def OnAccept(self, event):
        self.Destroy()

    def OnClose(self, event):
        self.Destroy()

    def OnBrowse(self, event):
        fd = wx.FileDialog(
            self,
            "Open",
            "",
            "",
            "",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fd.ShowModal()
        p = fd.GetPath()
        if p:
            b = event.GetEventObject()
            c = self.bindings[b]
            c.SetValue(p)
        fd.Destroy()

    def set_editors(self, editors=[]):
        le = len(editors)
        for i in range(le):
            e = editors[i]
            (l, c) = e
            self.labels[i].SetValue(l)
            self.commands[i].SetValue(c)

    def get_editors(self):
        editors = []
        for i in range(10):
            l = self.labels[i].GetValue()
            c = self.commands[i].GetValue()
            if l and c:
                editors.append((l, c))
        return editors


class HSettings(wx.Dialog):
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
        self.masks.Bind(wx.EVT_CHECKBOX, self.toggle_filemasks)
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
            )
        sbs.Add(self.bg_white)
        self.bg_black = wx.RadioButton(
            panel,
            label='Black',
            )
        sbs.Add(self.bg_black)
        self.bg_checkered = wx.RadioButton(
            panel,
            label='Checkered',
            )
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

    def toggle_filemasks(self, event):
        self.entry.Enable(self.masks.GetValue())

    def is_centered(self):
        return self.se_centered.GetValue()

    def set_centered(self, centered=True):
        self.se_centered.SetValue(centered)

    def is_aspect(self):
        return self.se_aspect.GetValue()

    def set_aspect(self, aspect=True):
        self.se_aspect.SetValue(aspect)

    def is_zoom(self):
        return self.se_zoom.GetValue()

    def set_zoom(self, zoom=True):
        self.se_zoom.SetValue(zoom)

    def set_usemask(self, usemask=True):
        self.masks.SetValue(usemask)
        self.entry.Enable(usemask)

    def is_usemask(self):
        return self.masks.GetValue()

    def get_filemasks(self):
        return self.entry.GetValue()

    def get_background(self):
        if self.bg_none.GetValue():
            return hvcommon.BACKGROUND_NONE
        elif self.bg_white.GetValue():
            return hvcommon.BACKGROUND_WHITE
        elif self.bg_black.GetValue():
            return hvcommon.BACKGROUND_BLACK
        elif self.bg_checkered.GetValue():
            return hvcommon.BACKGROUND_CHECKERED
        else:
            return hvcommon.BACKGROUND_NONE

    def set_background(self, background):
        if background == hvcommon.BACKGROUND_WHITE:
            self.bg_white.SetValue(True)
        elif background == hvcommon.BACKGROUND_BLACK:
            self.bg_black.SetValue(True)
        elif background == hvcommon.BACKGROUND_CHECKERED:
            self.bg_checkered.SetValue(True)
        else:
            self.bg_none.SetValue(True)

    def set_filemasks(self, masks):
        if masks:
            self.entry.SetValue(masks)
            self.masks.SetValue(True)

    def set_shrink(self, shrink=True):
        self.se_shrink.SetValue(shrink)

    def is_shrink(self):
        return self.se_shrink.GetValue()

    def get_config(self):
        config = {}
        config['filemasks'] = self.get_filemasks()
        config['centered'] = self.is_centered()
        config['aspect'] = self.is_aspect()
        config['maximize'] = self.is_zoom()
        config['shrink'] = self.is_shrink()
        config['usemask'] = self.is_usemask()
        config['background'] = "%(b)d" % {'b': self.get_background()}
        return config

    def set_config(self, config={}):
        if 'filemasks' in config:
            self.set_filemasks(config['filemasks'])
        if 'centered' in config:
            self.set_centered(config['centered'])
        if 'aspect' in config:
            self.set_aspect(config['aspect'])
        if 'maximize' in config:
            self.set_zoom(config['maximize'])
        if 'shrink' in config:
            self.set_shrink(config['shrink'])
        if 'usemask' in config:
            self.set_usemask(config['usemask'])
        if 'background' in config:
            try:
                bg = int(config['background'])
                self.set_background(bg)
            except ValueError:
                self.set_background(hvcommon.BACKGROUND_NONE)
        if 'editors' in config:
            self.editors = config['editors']

    def OnAccept(self, event):
        self.Destroy()

    def OnClose(self, event):
        self.Destroy()


class HWindow(wx.Frame):
    def __init__(self, startupobj):
        wx.Frame.__init__(
            self,
            None,
            title="/hv/",
            size=(800, 600))
        self.masks = []
        self.flip_x = False
        self.flip_y = False
        self.rotate = 0
        self.settings = {}
        self.masks = []
        self.editors = []
        self.current = None
        self.origin = None
        self.picture = None
        self.create_ui(startupobj)

    def create_ui(self, startupobj=None):
        submenu = wx.Menu()
        subitem = submenu.Append(
            -1,
            "&Preferences\tCtrl-P",
            "Show preferences dialog")
        self.Bind(wx.EVT_MENU, self.show_settings, subitem)
        subitem = submenu.Append(
            -1,
            "&Editors\tCtrl-E",
            "Show editors dialog")
        self.Bind(wx.EVT_MENU, self.show_editors, subitem)
        subitem = submenu.Append(wx.ID_SEPARATOR)
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
            wx.LC_REPORT | wx.LC_VRULES)
        self.dirList.InsertColumn(0, 'Directory name')
        self.dirList.InsertColumn(1, 'Date')
        self.dirList.InsertColumn(2, 'Size')
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
        self.image = HvImage(self.splitterV)
        self.splitterV.SplitVertically(self.splitterH, self.image, 250)
        self.CreateStatusBar()
        self.SetStatusText("/hv/")

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

    def update_title(self):
        self.SetTitle("%(d)s - /hv/" % {'d': os.getcwd()})

    def display_file(self, filename):
        self.image.display_file(filename)

    def get_configuration(self):
        configuration = {}
        configuration['window'] = {}
        (x, y) = self.GetPosition()
        configuration['window']['x'] = "%(x)d" % {'x': x}
        configuration['window']['y'] = "%(y)d" % {'y': y}
        (w, h) = self.GetSize()
        configuration['window']['w'] = "%(w)d" % {'w': w}
        configuration['window']['h'] = "%(h)d" % {'h': h}
        configuration['browser'] = {}
        configuration['browser']['lastdir'] = os.getcwd()
        # r = self.sv1.get_allocation()
        # configuration['browser']['w'] = "%(w)d" % {'w': r.width}
        # configuration['browser']['h'] = "%(h)d" % {'h': r.height}
        configuration['settings'] = self.settings
        configuration['editors'] = {}
        for i in range(len(self.editors)):
            (name, command) = self.editors[i]
            if name and command:
                configuration['editors']['name%(n)d' % {'n': i}] = name
                configuration['editors']['command%(n)d' % {'n': i}] = command
        return configuration

    def OnSelectFileList(self, event):
        item = event.GetItem()
        text = item.GetText()
        self.display_file(text)

    def OnDblClickDirList(self, event):
        dname = event.GetItem().GetText()
        if not dname:
            dname = "."
        self.read_dir(dname)

    def show_editors(self, event):
        e = HEditors(self)
        e.set_editors(self.editors)
        r = e.ShowModal()
        if r == wx.ID_OK:
            self.editors = e.get_editors()
        e.Destroy()

    def OnExit(self, event):
        hvcommon.saveconfig(self.get_configuration())
        self.Close(True)

    def OnAbout(self, event):
        ab = wx.MessageDialog(
            self,
            "hv\nwxPython image viewer\n(C) Marcin Bielewicz, 2017-?",
            "About hv",
            wx.OK | wx.ICON_INFORMATION)
        ab.ShowModal()
        ab.Destroy()

    def show_settings(self, event):
        s = HSettings(self)
        s.set_config(self.settings)
        r = s.ShowModal()
        if r == wx.ID_OK:
            self.settings = s.get_config()
            self.masks = []
            if 'filemasks' in self.settings:
                if self.settings['filemasks']:
                    for mask in self.settings['filemasks'].split("|"):
                        if mask:
                            self.masks.append(mask)
            self.read_dir()
            self.image.display()
        s.Destroy()

    def set_configuration(self, configuration={}, chdir=False):
        try:
            x = int(configuration['window']['x'])
            y = int(configuration['window']['y'])
            self.Move(wx.Point(x, y))
        except KeyError:
            pass
        try:
            w = int(configuration['window']['w'])
            h = int(configuration['window']['h'])
            self.SetSize(wx.Size(w, h))
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
        # try:
        #     w = int(configuration['browser']['w'])
        #     h = int(configuration['browser']['h'])
        #     self.sv1.set_size_request(w, h)
        # except KeyError:
        #     pass
        try:
            self.settings = configuration['settings']
        except KeyError:
            pass
        if 'filemasks' in self.settings:
            self.masks = self.settings['filemasks'].split("|")
        if 'editors' in configuration:
            self.editors = configuration['editors']
        else:
            self.editors = []
        self.update_editors()

    def update_editors(self):
        pass

    def read_dir(self, dirname="."):
        if not dirname:
            dirname = "."
        os.chdir(dirname)

        self.fileList.DeleteAllItems()
        self.dirList.DeleteAllItems()

        masks = self.masks if self.settings['usemask'] else []
        for f in hvcommon.getfiles(".", masks):
            self.fileList.Append((f[0], f[2], f[1]))

        for d in hvcommon.getdirs_full():
            self.dirList.Append((d[0], d[1], d[2]))

        for drive in hvcommon.get_drives():
            self.dirList.Append((
                "%(letter)s:\\"
                % {'letter': drive}, '', ''))
        self.update_title()


if __name__ == "__main__":
    try:
        so = sys.argv[1]
    except IndexError:
        so = None
    app = wx.App()
    hw = HWindow(so)
    hw.read_dir()

    hw.Show()
    app.MainLoop()
