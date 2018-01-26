#!/usr/bin/env python

import gtk
import gobject
import mimetypes
import os
import sys
import glib
import zipfile
import hvcommon

try:
    import numpy
    import PIL.Image
except ImportError:
    pass

try:
    import rsvg
except ImportError:
    pass


def read_generic_image(filename):
    try:
        fh = open(filename, "rb")
        data = fh.read()
        fh.close()
        loader = gtk.gdk.PixbufLoader()
        if loader.write(data):
            pixbuf = loader.get_pixbuf()
            loader.close()
            return pixbuf
    except IOError:
        pass
    except glib.GError:
        pass
    return None


def read_xpm_pixbuf(filename):
    try:
        return gtk.gdk.pixbuf_new_from_file(filename)
    except IOError:
        pass
    except glib.GError:
        pass
    return None


def read_pillow_file(filename):
    try:
        im = PIL.Image.open(filename)
        data = numpy.array(im)
        w, h = im.size
        pix = gtk.gdk.pixbuf_new_from_array(
            data,
            gtk.gdk.COLORSPACE_RGB,
            8)
        return pix
    except NameError:
        pass
    except IOError:
        pass
    return None


def read_idraw_pillow(filename):
    try:
        zf = zipfile.ZipFile(filename)
        tn = "Thumbnails/Preview.jpg"
        fh = zf.open(tn)
        im = PIL.Image.open(fh)
        data = numpy.array(im)
        pix = gtk.gdk.pixbuf_new_from_array(
            data,
            gtk.gdk.COLORSPACE_RGB,
            8)
        fh.close()
        return pix
    except NameError:
        pass
    except KeyError:
        pass
    except zipfile.BadZipfile:
        pass
    except IOError:
        pass
    return None


def read_jpeg_pixbuf(filename):
    fh = open(filename, "rb")
    data = fh.read()
    fh.close()
    try:
        loader = gtk.gdk.PixbufLoader()
        if loader.write(data):
            pixbuf = loader.get_pixbuf()
            loader.close()
            return pixbuf
    except glib.GError:
        pass
    except IOError:
        pass
    return None


def read_jpeg_file(filename):
    pixbuf = read_jpeg_pixbuf(filename)
    if not pixbuf:
        pixbuf = read_pillow_file(filename)
    return pixbuf


def read_idraw_pixbuf(filename):
    try:
        zf = zipfile.ZipFile(filename)
        tn = "Thumbnails/Preview.jpg"
        data = zf.read(tn)
        loader = gtk.gdk.PixbufLoader()
        if loader.write(data):
            pixbuf = loader.get_pixbuf()
            loader.close()
            if not pixbuf:
                data = numpy.array(data)
                pixbuf = gtk.gdk.pixbuf_new_from_array(
                    data,
                    gtk.gdk.COLORSPACE_RGB,
                    8)
            return pixbuf
    except KeyError:
        pass
    except zipfile.BadZipfile:
        pass
    except TypeError:
        pass
    except IOError:
        pass
    return None


def read_idraw_file(filename):
    pixbuf = read_idraw_pixbuf(filename)
    if not pixbuf:
        pixbuf = read_idraw_pillow(filename)
    return pixbuf


def read_svg_file(filename):
    try:
        handle = rsvg.Handle(filename)
        pixbuf = handle.get_pixbuf()
        return pixbuf
    except IOError:
        pass
    except OSError:
        pass
    except glib.GError:
        pass
    except NameError:
        pass
    return None


image_loaders = {
    'generic_image': read_generic_image,
    '.idraw': read_idraw_file,
    '.svg': read_svg_file,
    '.jpg': read_jpeg_file,
    '.bmp': read_pillow_file,
    '.xpm': read_xpm_pixbuf,
    '.jpeg': read_jpeg_file}


def read_image(filename):
    try:
        suf = os.path.splitext(
            os.path.basename(
                filename))[1].lower()
    except IndexError:
        suf = None
    if suf in image_loaders:
        return image_loaders[suf](filename)
    else:
        return read_generic_image(filename)


class HSettings(gtk.Dialog):

    def __init__(self):
        gtk.Dialog.__init__(self,
                            "Preferences",
                            None,
                            gtk.DIALOG_MODAL,
                            (gtk.STOCK_CANCEL,
                             gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK,
                             gtk.RESPONSE_ACCEPT))
        frame = gtk.Frame(label="Accepted file masks")
        self.vbox.pack_start(frame)
        vbox = gtk.VBox()
        frame.add(vbox)
        self.masks = gtk.CheckButton("Accept following file masks:")
        self.masks.connect("toggled", self.toggle_filemasks)
        vbox.pack_start(self.masks)
        self.entry = gtk.Entry()
        self.entry.set_text(hvcommon.DEFAULT_MASKS)
        self.entry.set_sensitive(False)
        vbox.pack_start(self.entry)
        hbox = gtk.HBox()
        self.vbox.pack_start(hbox)
        vbox1 = gtk.VBox()
        hbox.pack_start(vbox1)
        frame = gtk.Frame(label="Background")
        vbox1.pack_start(frame)
        vbox = gtk.VBox()
        frame.add(vbox)
        self.radio1 = gtk.RadioButton(None, "None")
        vbox.pack_start(self.radio1)
        self.radio2 = gtk.RadioButton(self.radio1, "White")
        vbox.pack_start(self.radio2)
        self.radio3 = gtk.RadioButton(self.radio1, "Black")
        vbox.pack_start(self.radio3)
        self.radio4 = gtk.RadioButton(self.radio1, "Checkered")
        vbox.pack_start(self.radio4)
        vbox1 = gtk.VBox()
        hbox.pack_start(vbox1)
        frame = gtk.Frame("Settings")
        vbox1.pack_start(frame)
        vbox = gtk.VBox()
        frame.add(vbox)
        self.centered = gtk.CheckButton("Centered")
        vbox.pack_start(self.centered)
        self.aspect = gtk.CheckButton("Keep aspect ratio")
        vbox.pack_start(self.aspect)
        self.maximize = gtk.CheckButton("Zoom to fit")
        vbox.pack_start(self.maximize)
        self.shrink = gtk.CheckButton("Shrink to fit")
        vbox.pack_start(self.shrink)
        self.set_title("Preferences")
        self.set_has_separator(True)
        self.set_size_request(640, 256)
        self.show_all()

    def toggle_filemasks(self, widget, data=None):
        self.entry.set_sensitive(self.masks.get_active())

    def is_centered(self):
        return self.centered.get_active()

    def set_centered(self, centered=True):
        self.centered.set_active(centered)

    def is_aspect(self):
        return self.aspect.get_active()

    def set_aspect(self, aspect=True):
        self.aspect.set_active(aspect)

    def is_maximize(self):
        return self.maximize.get_active()

    def set_maximize(self, maximize=True):
        self.maximize.set_active(maximize)

    def get_filemasks(self):
        return self.entry.get_text() if self.masks.get_active() else ""

    def get_background(self):
        if self.radio1.get_active():
            return hvcommon.BACKGROUND_NONE
        elif self.radio2.get_active():
            return hvcommon.BACKGROUND_WHITE
        elif self.radio3.get_active():
            return hvcommon.BACKGROUND_BLACK
        elif self.radio4.get_active():
            return hvcommon.BACKGROUND_CHECKERED
        else:
            return hvcommon.BACKGROUND_NONE

    def set_background(self, background):
        if background == hvcommon.BACKGROUND_WHITE:
            self.radio2.set_active(True)
        elif background == hvcommon.BACKGROUND_BLACK:
            self.radio3.set_active(True)
        elif background == hvcommon.BACKGROUND_CHECKERED:
            self.radio4.set_active(True)
        else:
            self.radio1.set_active(True)

    def set_filemasks(self, masks):
        if masks:
            self.entry.set_text(masks)
            self.masks.set_active(True)

    def set_shrink(self, shrink=True):
        self.shrink.set_active(shrink)

    def is_shrink(self):
        return self.shrink.get_active()

    def get_config(self):
        config = {}
        config['filemasks'] = self.get_filemasks()
        config['centered'] = self.is_centered()
        config['aspect'] = self.is_aspect()
        config['maximize'] = self.is_maximize()
        config['shrink'] = self.is_shrink()
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
            self.set_maximize(config['maximize'])
        if 'shrink' in config:
            self.set_shrink(config['shrink'])
        if 'background' in config:
            try:
                bg = int(config['background'])
                self.set_background(bg)
            except ValueError:
                self.set_background(hvcommon.BACKGROUND_NONE)


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
        configuration['browser']['w'] = "%(w)d" % {'w': r.width}
        configuration['browser']['h'] = "%(h)d" % {'h': r.height}
        configuration['settings'] = self.settings
        return configuration

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
            w = int(configuration['browser']['w'])
            h = int(configuration['browser']['h'])
            self.sv1.set_size_request(w, h)
        except KeyError:
            pass
        try:
            self.settings = configuration['settings']
        except KeyError:
            pass
        if 'filemasks' in self.settings:
            self.masks = self.settings['filemasks'].split("|")

    def read_dir(self, dirname="."):
        if not dirname:
            dirname = "."
        os.chdir(dirname)
        self.filemodel.clear()
        self.dirmodel.clear()

        for f in hvcommon.getfiles(dirname, self.masks):
            self.filemodel.append([self.file_icon, f[0], f[1], f[2]])

        self.dirmodel.append([self.dir_icon, "."])
        self.dirmodel.append([self.dir_icon, ".."])

        for d in hvcommon.getdirs(dirname):
            self.dirmodel.append([self.dir_icon, d])

        for drive in hvcommon.get_drives():
            self.dirmodel.append(
                [self.drive_icon,
                 "%(letter)s:\\" % {'letter': drive}])

    def __init__(self, startupobj=""):
        self.settings = {}
        self.masks = []
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.connect("destroy", self.quit)
        self.origin = None
        self.picture = None
        self.create_ui(startupobj)

    def quit(self, data=None):
        hvcommon.saveconfig(self.get_configuration())
        gtk.main_quit()

    def dir_activated(self, treeview, path, column, user_data=None):
        sel = treeview.get_selection()
        (model, iter) = sel.get_selected()
        newdir = os.path.join(os.getcwd(), model[iter][1])
        self.read_dir(newdir)
        self.update_title()

    def file_activated(self, treeview, path, column, user_data=None):
        sel = treeview.get_selection()
        (model, iter) = sel.get_selected()
        if iter is not None:
            print("Activated %(it)s"
                  % {'it': model[iter][1]})

    def display_file(self, filename):
        (type, encoding) = mimetypes.guess_type(filename)
        if not type:
            type = "unknown"
        status = "File: %(fn)s, type: %(ty)s" \
                 % {
                     'fn': filename,
                     'ty': type}
        if not encoding:
            encoding = "unspecified"
        status = "%(st)s, encoding: %(enc)s" \
                 % {'st': status,
                    'enc': encoding}
        pixbuf = read_image(filename)
        if pixbuf:
            self.picture = pixbuf
            self.origin = pixbuf
        else:
            self.picture = None
            self.origin = None
        self.display()
        self.statusbar.push(0, status)

    def rotate_left(self):
        self.picture = self.picture.rotate_simple(90)
        self.display()

    def rotate_right(self):
        self.picture = self.picture.rotate_simple(270)
        self.display()

    def reload(self):
        self.picture = self.origin
        self.display()

    def flip_horiz(self):
        self.picture = self.picture.flip(True)
        self.display()

    def flip_vert(self):
        self.picture = self.picture.flip(False)
        self.display()

    def display(self):
        if 'background' in self.settings:
            background = int(self.settings['background'])
        else:
            background = hvcommon.BACKGROUND_NONE

        centered = False
        if 'centered' in self.settings:
            if self.settings['centered']:
                centered = True
            else:
                centered = False
        else:
            centered = True

        if centered:
            self.image.set_alignment(0.5, 0.5)
        else:
            self.image.set_alignment(0, 0)

        if self.picture:
            r = self.image.get_allocation()
            pw = self.picture.get_width()
            ph = self.picture.get_height()
            (w, h) = hvcommon.get_max_rect(
                r.width,
                r.height,
                pw,
                ph)
            pb = gtk.gdk.Pixbuf(
                gtk.gdk.COLORSPACE_RGB,
                True,
                8,
                w,
                h)
            self.image.clear()
            if background == hvcommon.BACKGROUND_WHITE:
                pb.fill(0xffffffff)
            elif background == hvcommon.BACKGROUND_BLACK:
                pb.fill(0x000000ff)
            elif background == hvcommon.BACKGROUND_CHECKERED:
                chk = gtk.gdk.pixbuf_new_from_xpm_data(hvcommon.checkers)
                tx = w / 100
                ty = h / 100
                if w % 100 > 0:
                    tx = tx + 1
                if h % 100 > 0:
                    ty = ty + 1

                for i in range(0, tx):
                    for j in range(0, ty):
                        wl = w - 100 * i
                        hl = h - 100 * j
                        wl = 100 if wl > 100 else wl
                        hl = 100 if hl > 100 else hl
                        chk.copy_area(0, 0, wl, hl, pb, i * 100, j * 100)

            if centered:
                (x, y) = hvcommon.get_location(w, h, pw, ph)
            else:
                x = 0
                y = 0
            self.picture.copy_area(0, 0, pw, ph, pb, x, y)
            self.image.set_from_pixbuf(pb)
        else:
            self.image.set_from_stock(
                gtk.STOCK_MISSING_IMAGE,
                gtk.ICON_SIZE_LARGE_TOOLBAR)

    def popup_image(self, widget, event, unused):
        if unused.get_visible():
            unused.hide()
        else:
            if event.type == gtk.gdk.BUTTON_PRESS:
                if event.button == 3:
                    unused.show_all()
                    unused.popup(
                        None,
                        None,
                        None,
                        event.button,
                        event.time)

    def file_changed(self, selection):
        (model, iter) = selection.get_selected()
        if iter is not None:
            filename = model[iter][1]
            fulln = os.path.join(os.getcwd(), filename)
            self.display_file(fulln)

    def show_settings(self, data=None):
        s_window = HSettings()
        s_window.set_config(self.settings)
        response = s_window.run()
        if response == gtk.RESPONSE_ACCEPT:
            self.settings = s_window.get_config()
            self.masks = []
            if 'filemasks' in self.settings:
                if self.settings['filemasks']:
                    for mask in self.settings['filemasks'].split("|"):
                        if mask:
                            self.masks.append(mask)
            self.read_dir()
            self.display()
        s_window.destroy()

    def click_flip_horiz(self, data=None):
        self.flip_horiz()

    def click_flip_vert(self, data=None):
        self.flip_vert()

    def click_rotate_cl(self, data=None):
        self.rotate_left()

    def click_rotate_cc(self, data=None):
        self.rotate_right()

    def create_ui(self, startupobj=""):

        self.imagemenu = gtk.Menu()
        menu_item = gtk.MenuItem("Flip _horizontally")
        menu_item.connect('activate', self.click_flip_horiz)
        self.imagemenu.append(menu_item)
        menu_item = gtk.MenuItem("Flip _vertically")
        menu_item.connect('activate', self.click_flip_vert)
        self.imagemenu.append(menu_item)
        menu_item = gtk.MenuItem("Rotate _clockwise")
        menu_item.connect('activate', self.click_rotate_cl)
        self.imagemenu.append(menu_item)
        menu_item = gtk.MenuItem("Rotate c_ounter-clockwise")
        menu_item.connect('activate', self.click_rotate_cc)
        self.imagemenu.append(menu_item)
        self.imagemenu.append(gtk.SeparatorMenuItem())
        menu_item = gtk.MenuItem("Open _with...")
        submenu = gtk.Menu()
        menu_item.set_submenu(submenu)
        self.imagemenu.append(menu_item)

        menu_bar = gtk.MenuBar()
        menu_item = gtk.MenuItem("_hv")
        menu = gtk.Menu()
        menu_item.set_submenu(menu)
        menu_subitem = gtk.MenuItem("_Preferences")
        menu_subitem.connect('activate', self.show_settings)
        menu.append(menu_subitem)
        menu_subitem = gtk.MenuItem("_Quit")
        menu_subitem.connect('activate', self.quit)
        menu.append(menu_subitem)
        menu_bar.append(menu_item)
        stock_hi = gtk.Image()
        self.drive_icon = stock_hi.render_icon(
            gtk.STOCK_HARDDISK,
            gtk.ICON_SIZE_MENU)

        stock_di = gtk.Image()
        self.dir_icon = stock_di.render_icon(
            gtk.STOCK_DIRECTORY,
            gtk.ICON_SIZE_MENU)
        dcolumn = gtk.TreeViewColumn("Directory name")
        dtext_renderer = gtk.CellRendererText()
        dicon_renderer = gtk.CellRendererPixbuf()
        dcolumn.pack_start(dicon_renderer, False)
        dcolumn.pack_start(dtext_renderer, False)
        dcolumn.set_attributes(dtext_renderer, text=1)
        dcolumn.set_attributes(dicon_renderer, pixbuf=0)

        self.file_icon = stock_di.render_icon(
            gtk.STOCK_FILE,
            gtk.ICON_SIZE_MENU)

        self.sv1 = gtk.ScrolledWindow()
        self.sv1.set_usize(150, 150)
        self.sv1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        sv2 = gtk.ScrolledWindow()
        sv2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.dirmodel = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING)
        self.filemodel = gtk.ListStore(
            gtk.gdk.Pixbuf,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING,
            gobject.TYPE_STRING)

        fcolumn = gtk.TreeViewColumn("Filename")
        ftext_renderer = gtk.CellRendererText()
        ficon_renderer = gtk.CellRendererPixbuf()
        fcolumn.pack_start(ficon_renderer, False)
        fcolumn.pack_start(ftext_renderer, False)
        fcolumn.set_attributes(ftext_renderer, text=1)
        fcolumn.set_attributes(ficon_renderer, pixbuf=0)

        fcolumn2 = gtk.TreeViewColumn("Size")
        ftext_renderer2 = gtk.CellRendererText()
        fcolumn2.pack_start(ftext_renderer2, False)
        fcolumn2.set_attributes(ftext_renderer2, text=3)
        fcolumn3 = gtk.TreeViewColumn("Last modified")
        ftext_renderer3 = gtk.CellRendererText()
        fcolumn3.pack_start(ftext_renderer3, False)
        fcolumn3.set_attributes(ftext_renderer3, text=2)

        self.dirlist = gtk.TreeView(self.dirmodel)
        self.dirlist.append_column(dcolumn)
        self.dirlist.connect('row-activated', self.dir_activated, None)

        self.filelist = gtk.TreeView(self.filemodel)
        self.filelist.append_column(fcolumn)
        self.filelist.append_column(fcolumn2)
        self.filelist.append_column(fcolumn3)
        self.filelist.connect('row-activated', self.file_activated, None)

        dirsel = self.dirlist.get_selection()
        dirsel.set_mode(gtk.SELECTION_SINGLE)
        filesel = self.filelist.get_selection()
        filesel.set_mode(gtk.SELECTION_SINGLE)
        filesel.connect('changed', self.file_changed)

        self.sv1.add_with_viewport(self.dirlist)
        sv2.add_with_viewport(self.filelist)

        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, "/hv/")

        hpaned = gtk.HPaned()
        vpaned = gtk.VPaned()

        vpaned.add1(self.sv1)
        vpaned.add2(sv2)

        hpaned.add1(vpaned)
        self.sv3 = gtk.ScrolledWindow()
        self.sv3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.evb = gtk.EventBox()
        self.image = gtk.Image()
        self.evb.add(self.image)
        self.sv3.add_with_viewport(self.evb)
        hpaned.add2(self.sv3)

        self.evb.connect(
            'button-press-event',
            self.popup_image,
            self.imagemenu)

        # Toolbar
        toolbar = gtk.Toolbar()
        icon = gtk.Image()
        icon.set_from_stock(
            gtk.STOCK_REFRESH,
            gtk.ICON_SIZE_LARGE_TOOLBAR)
        toolbar.append_item(
            "Reload",
            "Reload image from disk",
            None,
            icon,
            self.reload)
        toolbar.append_space()

        vbox = gtk.VBox(False, 2)
        vbox.pack_start(menu_bar, False, False, 0)
        vbox.pack_start(toolbar, False, False, 0)
        vbox.pack_start(hpaned, True, True, 1)
        vbox.pack_start(self.statusbar, False, False, 0)

        self.add(vbox)
        self.resize(800, 600)

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
        self.show_all()

    def update_title(self):
        self.set_title("%(d)s - /hv/" % {'d': os.getcwd()})


if __name__ == "__main__":
    try:
        so = sys.argv[1]
    except IndexError:
        so = ""
    hw = HWindow(so)
    hw.show()
    try:
        gtk.main()
    except KeyboardInterrupt:
        print("Bye!")
