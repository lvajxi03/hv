#!/usr/bin/env python

import gtk, gobject, mimetypes
import os


import ConfigParser

have_windows = False

try:
    import string
    from ctypes import windll
    have_windows = True
except ImportError as ie:
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

def getfiles(curdir = "."):
    return [f for f in os.listdir(curdir) if os.path.isfile(f)]

def getdirs(curdir = "."):
    return [f for f in os.listdir(curdir) if os.path.isdir(f)]

def saveconfig(configuration = {}):
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
    except IOError as ioe:
        pass
    return configuration

class HWindow(gtk.Window):

    def get_configuration(self):
        configuration = {}
        configuration['window'] = {}
        (x, y) = self.get_position()
        configuration['window']['x'] = "%(x)d" % {'x': x}
        configuration['window']['y'] = "%(y)d" % {'y': y}
        (w, h) = self.get_size()
        configuration['window']['w'] = "%(w)d" % {'w': w}
        configuration['window']['h'] = "%(h)d" % {'h': h}
        configuration['browser'] = {}
        configuration['browser']['lastdir'] = os.getcwd()
        r = self.sv1.get_allocation()
#        (w, h) = self.sv1.size_request()
        configuration['browser']['w'] = "%(w)d" % {'w': r.width}
        configuration['browser']['h'] = "%(h)d" % {'h': r.height}
        return configuration

    def set_configuration(self, configuration = {}):
        try:
            x = int(configuration['window']['x'])
            y = int(configuration['window']['y'])
            self.move(x, y)
        except KeyError as ke:
            pass
        try:
            w = int(configuration['window']['w'])
            h = int(configuration['window']['h'])
            self.resize(w, h)
        except KeyError as ke:
            pass
        try:
            ld = configuration['browser']['lastdir']
            os.chdir(configuration['browser']['lastdir'])
        except KeyError as ke:
            pass
        except IOError as ioe:
            pass
        try:
            w = int(configuration['browser']['w'])
            h = int(configuration['browser']['h'])
            self.sv1.set_size_request(w, h)
        except KeyError as ke:
            pass

    def read_dir(self, dirname = "."):
        self.filemodel.clear()
        self.dirmodel.clear()

        for f in getfiles(dirname):
            self.filemodel.append([f])
        self.dirmodel.append(["."])
        self.dirmodel.append([".."])
        for d in getdirs(dirname):
            self.dirmodel.append([d])
        for drive in get_drives():
            self.dirmodel.append(["%(letter)s:\\" % {'letter': drive}])

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.create_ui()

    def quit(self, data = None):
        saveconfig(self.get_configuration())
        gtk.main_quit()

    def dir_activated(self, treeview, path, column, user_data = None):
        sel = treeview.get_selection()
        (model, iter) = sel.get_selected()
        # Dirname is under model[iter][0]
        newdir = os.path.join(os.getcwd(), model[iter][0])
        os.chdir(newdir)
        self.read_dir()
        self.set_title("%(d)s - /hv/" % {'d': os.getcwd()})

    def file_activated(self, treeview, path, column, user_data = None):
        sel = treeview.get_selection()
        (model, iter) = sel.get_selected()
        if iter is not None:
            print "Activated", model[iter][0]

    def file_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is not None:
            filename = model[iter][0]
            fulln = os.path.join(os.getcwd(), filename)
            (type, encoding) = mimetypes.guess_type(fulln)
            if type is not None:
                status = "File: %(fn)s, type: %(ty)s" % {'fn': fulln, 'ty': type}
                if encoding is not None:
                    status = "%(st)s, encoding: %(enc)s" % {'st': status, 'enc': encoding}
                if type.startswith("image/"):
                    self.image.set_from_file(fulln)
            else:
                status = "File: %(fn)s, type: %(ty)s" % {'fn': fulln, 'ty': 'unknown'}
            self.statusbar.push(0, status)

    def create_ui(self):
        menu_bar = gtk.MenuBar()
        menu_item = gtk.MenuItem("_File")
        menu = gtk.Menu()
        menu_item.set_submenu(menu)
        menu_subitem = gtk.MenuItem("_Quit")
        menu_subitem.connect('activate', self.quit)
        menu.append(menu_subitem)
        menu_bar.append(menu_item)

        self.sv1 = gtk.ScrolledWindow()
        self.sv1.set_usize(150, 150)
        self.sv1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        sv2 = gtk.ScrolledWindow()
        sv2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.dirmodel = gtk.ListStore(gobject.TYPE_STRING)
        self.filemodel = gtk.ListStore(gobject.TYPE_STRING)

        self.dirlist = gtk.TreeView(self.dirmodel)
        self.dirlist.connect('row-activated', self.dir_activated, None)

        self.filelist = gtk.TreeView(self.filemodel)
        self.filelist.connect('row-activated', self.file_activated, None)

        dirsel = self.dirlist.get_selection()
        dirsel.set_mode(gtk.SELECTION_SINGLE)
        filesel = self.filelist.get_selection()
        filesel.set_mode(gtk.SELECTION_SINGLE)
        filesel.connect('changed', self.file_changed)

        ren1 = gtk.CellRendererText()
        col1 = gtk.TreeViewColumn("Directory name", ren1, text = 0)
        self.dirlist.append_column(col1)
        ren2 = gtk.CellRendererText()
        col2 = gtk.TreeViewColumn("File name", ren2, text = 0)
        self.filelist.append_column(col2)

        self.sv1.add_with_viewport(self.dirlist)
        sv2.add_with_viewport(self.filelist)

        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, "/hv/")

        self.image = gtk.Image()

        hpaned = gtk.HPaned()
        vpaned = gtk.VPaned()

        vpaned.add1(self.sv1)
        vpaned.add2(sv2)

        hpaned.add1(vpaned)
        hpaned.add2(self.image)

        vbox = gtk.VBox(False, 2)
        vbox.pack_start(menu_bar, False, False, 0)
        vbox.pack_start(hpaned, True, True, 1)
        vbox.pack_start(self.statusbar, False, False, 0)

        self.add(vbox)
        self.set_title("%(d)s - /hv/" % {'d': os.getcwd()})
        self.resize(800, 600)

        self.show_all()
        self.set_configuration(readconfig())
        self.read_dir()

if __name__ == "__main__":
    hw = HWindow()
    hw.show()
    gtk.main()
