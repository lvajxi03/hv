#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import GLib

import mimetypes
import os
import sys
import glib
import zipfile
import subprocess
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
        loader = GdkPixbuf.PixbufLoader()
        if loader.write(data):
            pixbuf = loader.get_pixbuf()
            loader.close()
            return pixbuf
    except IOError:
        pass
    except GLib.Error:
        pass
    return None


def read_xpm_pixbuf(filename):
    try:
        return GdkPixbuf.pixbuf_new_from_file(filename)
    except IOError:
        pass
    except GLib.Error:
        pass
    return None


def read_pillow_file(filename):
    try:
        im = PIL.Image.open(filename)
        data = numpy.array(im)
        w, h = im.size
        pix = GdkPixbuf.pixbuf_new_from_array(
            data,
            GdkPixbuf.Colorspace.RGB,
            8)
        return pix
    except NameError:
        pass
    except IOError:
        pass
    except GLib.Error:
        pass
    return None


def read_idraw_pillow(filename):
    try:
        zf = zipfile.ZipFile(filename)
        tn = "Thumbnails/Preview.jpg"
        fh = zf.open(tn)
        im = PIL.Image.open(fh)
        data = numpy.array(im)
        pix = GdkPixbuf.pixbuf_new_from_array(
            data,
            GdkPixbuf.Colorspace.RGB,
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
    except GLib.Error:
        pass
    return None


def read_jpeg_pixbuf(filename):
    fh = open(filename, "rb")
    data = fh.read()
    fh.close()
    try:
        loader = GdkPixbuf.PixbufLoader()
        if loader.write(data):
            pixbuf = loader.get_pixbuf()
            loader.close()
            return pixbuf
    except IOError:
        pass
    except GLib.Error:
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
        loader = GdkPixbuf.PixbufLoader()
        if loader.write(data):
            pixbuf = loader.get_pixbuf()
            loader.close()
            if not pixbuf:
                data = numpy.array(data)
                pixbuf = GdkPixbuf.pixbuf_new_from_array(
                    data,
                    GdkPixbuf.Colorspace.RGB,
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
    except GLib.Error:
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
    except NameError:
        pass
    except GLib.Error:
        pass
    return None


image_loaders = {
    'generic_image': read_generic_image,
    '.idraw': read_idraw_file,
    '.svg': read_svg_file,
    '.jpg': read_jpeg_file,
    '.bmp': read_pillow_file,
    '.png': read_pillow_file,
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


class HEditors(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self,
                            "Editors",
                            parent,
                            Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CANCEL,
                             Gtk.ResponseType.REJECT,
                             Gtk.STOCK_OK,
                             Gtk.ResponseType.ACCEPT))
        self.editors = []
        self.names = []
        self.commands = []
        frame = Gtk.Frame(label="Available editors")
        self.vbox.pack_start(frame, True, True, 3)
        table = Gtk.Table(10, 6)
        frame.add(table)
        for i in range(10):
            label = Gtk.Label("Label: ")
            table.attach(label, 0, 1, i, i+1)
            entry = Gtk.Entry()
            self.names.append(entry)
            table.attach(entry, 1, 2, i, i+1)
            label = Gtk.Label("Command: ")
            table.attach(label, 2, 3, i, i+1)
            entry = Gtk.Entry()
            self.commands.append(entry)
            table.attach(entry, 3, 5, i, i+1)
            button = Gtk.Button("...")
            button.connect('clicked', self.click_browse, i)
            table.attach(button, 5, 6, i, i+1)
        self.show_all()

    def set_editors(self, editors=[]):
        i = 0
        for name, command in editors:
            self.commands[i].set_text(command)
            self.names[i].set_text(name)
            i += 1

    def get_editors(self):
        editors = []
        for i in range(10):
            name = self.names[i].get_text()
            command = self.commands[i].get_text()
            if name and command:
                editors.append((name, command))
        return editors

    def click_browse(self, widget, data=None):
        dlg = Gtk.FileChooserDialog(
            "Find a program",
            self,
            Gtk.DialogFlags.MODAL | Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dlg.run()
        if response == Gtk.ResponseType.OK:
            self.commands[data].set_text(dlg.get_filename())
        dlg.destroy()


class HSettings(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self,
                            "Preferences",
                            parent,
                            Gtk.DialogFlags.MODAL,
                            (Gtk.STOCK_CANCEL,
                             Gtk.ResponseType.REJECT,
                             Gtk.STOCK_OK,
                             Gtk.ResponseType.ACCEPT))
        frame = Gtk.Frame(label="Accepted file masks")
        self.vbox.pack_start(frame, True, True, 3)
        vbox = Gtk.VBox()
        frame.add(vbox)
        self.masks = Gtk.CheckButton("Accept following file masks:")
        self.masks.connect("toggled", self.toggle_filemasks)
        vbox.pack_start(self.masks, True, False, 1)
        self.entry = Gtk.Entry()
        self.entry.set_text(hvcommon.DEFAULT_MASKS)
        self.entry.set_sensitive(False)
        vbox.pack_start(self.entry, True, True, 1)
        hbox = Gtk.HBox()
        self.vbox.pack_start(hbox, True, True, 1)
        vbox1 = Gtk.VBox()
        hbox.pack_start(vbox1, True, True, 1)
        frame = Gtk.Frame(label="Background")
        vbox1.pack_start(frame, True, True, 3)
        vbox = Gtk.VBox()
        frame.add(vbox)
        self.radio1 = Gtk.RadioButton.new_with_label_from_widget(None, "None")
        vbox.pack_start(self.radio1, False, False, 1)
        self.radio2 = Gtk.RadioButton.new_with_label_from_widget(
            self.radio1,
            "White")
        vbox.pack_start(self.radio2, False, False, 1)
        self.radio3 = Gtk.RadioButton.new_with_label_from_widget(
            self.radio1,
            "Black")
        vbox.pack_start(self.radio3, False, False, 1)
        self.radio4 = Gtk.RadioButton.new_with_label_from_widget(
            self.radio1,
            "Checkered")
        vbox.pack_start(self.radio4, False, False, 1)
        vbox1 = Gtk.VBox()
        hbox.pack_start(vbox1, True, True, 1)
        frame = Gtk.Frame(label="Settings")
        vbox1.pack_start(frame, True, True, 1)
        vbox = Gtk.VBox()
        frame.add(vbox)
        self.centered = Gtk.CheckButton("Centered")
        vbox.pack_start(self.centered, False, False, 1)
        self.aspect = Gtk.CheckButton("Keep aspect ratio")
        vbox.pack_start(self.aspect, False, False, 1)
        self.maximize = Gtk.CheckButton("Zoom to fit")
        vbox.pack_start(self.maximize, False, False, 1)
        self.shrink = Gtk.CheckButton("Shrink to fit")
        vbox.pack_start(self.shrink, False, False, 1)
        self.set_title("Preferences")
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
        if 'editors' in config:
            self.editors = config['editors']


class HWindow(Gtk.ApplicationWindow):

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
        configuration['editors'] = {}
        for i in range(len(self.editors)):
            (name, command) = self.editors[i]
            if name and command:
                configuration['editors']['name%(n)d' % {'n': i}] = name
                configuration['editors']['command%(n)d' % {'n': i}] = command
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
        if 'editors' in configuration:
            self.editors = configuration['editors']
        self.update_editors()

    def click_open_with(self, widget, data=None):
        if data and self.current:
            try:
                subprocess.Popen([data, self.current])
            except OSError as oe:
                ed = Gtk.MessageDialog(
                    self,
                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CLOSE,
                    "Error launching editor %(ed)s: %(er)s" %
                    {'ed': data, 'er': str(oe)})
                ed.set_title("Error")
                ed.run()
                ed.destroy()

    def update_editors(self):
        for item in self.editors_submenu:
            self.editors_submenu.remove(item)
        for name, command in self.editors:
            menu_item = Gtk.MenuItem(name)
            menu_item.set_property('use-underline', True)
            menu_item.connect('activate', self.click_open_with, command)
            self.editors_submenu.append(menu_item)

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

        self.update_title()

    def __init__(self, startupobj=""):
        self.flip_x = False
        self.flip_y = False
        self.rotate = 0
        self.settings = {}
        self.masks = []
        self.editors = []
        self.current = None
        Gtk.ApplicationWindow.__init__(self)
        self.set_property("show-menubar", True)
        self.connect("destroy", self.quit)
        self.origin = None
        self.picture = None
        self.create_ui(startupobj)

    def quit(self, data=None):
        hvcommon.saveconfig(self.get_configuration())
        Gtk.main_quit()

    def dir_activated(self, treeview, path, column, user_data=None):
        sel = treeview.get_selection()
        (model, iter) = sel.get_selected()
        newdir = os.path.join(os.getcwd(), model[iter][1])
        self.read_dir(newdir)

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
        self.statusbar.push(self.context_id, status)
        self.current = filename
        self.rotate = 0
        self.flip_x = 0
        self.flip_y = 0
        self.display()

    def rotate_left(self):
        self.rotate += 1
        self.rotate = self.rotate % 4
        self.display()

    def rotate_right(self):
        self.rotate -= 1
        self.rotate = self.rotate % 4
        self.display()

    def reload(self):
        self.picture = self.origin
        self.display()

    def flip_horiz(self):
        self.flip_x = not self.flip_x
        self.display()

    def flip_vert(self):
        self.flip_y = not self.flip_y
        self.display()

    def display(self, event=None, data=None):
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

        # Some default settings:
        if not 'aspect' in self.settings:
            self.settings['aspect'] = True
        if not 'shrink' in self.settings:
            self.settings['shrink'] = False
        if not 'maximize' in self.settings:
            self.settings['maximize'] = False
        self.picture = self.origin
        if self.picture:
            self.image.set_size_request(1, 1)
            self.sv3.set_size_request(1, 1)
            self.picture = self.picture.rotate_simple(self.rotate * 90)
            if self.flip_x:
                self.picture = self.picture.flip(True)
            if self.flip_y:
                self.picture = self.picture.flip(False)
            r = self.sv3.get_allocation()
            rw = r.width
            rh = r.height
            pw = self.picture.get_width()
            ph = self.picture.get_height()

            if centered:
                self.image.set_alignment(0.5, 0.5)
            else:
                self.image.set_alignment(0, 0)

            shrink = False
            zoom = False
            bigger = hvcommon.is_bigger_than_dp(
                pw,
                ph,
                rw,
                rh)
            aspect = self.settings['aspect']
            if bigger and self.settings['shrink']:
                (pw, ph) = hvcommon.calculate_shrink(
                    pw,
                    ph,
                    rw,
                    rh,
                    aspect)
                shrink = True
            elif not bigger and self.settings['maximize']:
                (pw, ph) = hvcommon.calculate_zoom(
                    pw,
                    ph,
                    rw,
                    rh,
                    aspect)
                zoom = True
            (w, h) = hvcommon.get_max_rect(
                rw,
                rh,
                pw,
                ph)
            if bigger and not zoom and not shrink:
                self.sv3.set_policy(
                    Gtk.PolicyType.AUTOMATIC,
                    Gtk.PolicyType.AUTOMATIC)
            else:
                self.sv3.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
            pb = GdkPixbuf.Pixbuf.new(
                GdkPixbuf.Colorspace.RGB,
                True,
                8,
                w,
                h)
            screen = self.get_screen()
            visual = screen.get_rgba_visual()
            if not visual:
                visual = screen.get_system_visual()
            # draw = self.image.get_window()
            # colormap = draw.get_colormap()
            pi = Gdk.Pixmap(draw, w, h, -1)
            pi.set_visual(visual)
            # pi.set_colormap(colormap)
            self.image.clear()
            if background == hvcommon.BACKGROUND_NONE:
                style = self.get_style()
                style = style.bg[Gtk.STATE_NORMAL]
                red = style.red / 256
                green = style.green / 256
                blue = style.blue / 256
                color = red * 65536 + green * 256 + blue
                color = color * 256 + 255
                pb.fill(color)
            elif background == hvcommon.BACKGROUND_WHITE:
                pb.fill(0xffffffff)
            elif background == hvcommon.BACKGROUND_BLACK:
                pb.fill(0x000000ff)
            elif background == hvcommon.BACKGROUND_CHECKERED:
                chk = GdkPixbuf.pixbuf_new_from_xpm_data(hvcommon.checkers)
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
            pi.draw_pixbuf(
                None,
                pb, 0, 0, 0, 0, w, h,
                Gdk.RGB_DITHER_NORMAL, 0, 0)

            if centered:
                (x, y) = hvcommon.get_location(w, h, pw, ph)
            else:
                x = 0
                y = 0
            if zoom or shrink:
                self.picture = self.picture.scale_simple(
                    pw, ph, Gdk.INTERP_BILINEAR)
            pi.draw_pixbuf(
                None,
                self.picture,
                0, 0, x, y, pw, ph,
                Gdk.RGB_DITHER_NORMAL, 0, 0)
            self.image.set_size_request(w, h)
            self.image.set_from_pixmap(pi, None)
        else:
            self.image.set_from_stock(
                Gtk.STOCK_MISSING_IMAGE,
                Gtk.IconSize.LARGE_TOOLBAR)

    def popup_image(self, widget, event, unused):
        if unused.get_visible():
            unused.hide()
        else:
            if event.button == 3:
                unused.show_all()
                unused.popup(
                    None,
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
        s_window = HSettings(self)
        s_window.set_config(self.settings)
        response = s_window.run()
        if response == Gtk.ResponseType.ACCEPT:
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

    def about_onclose(self, action, parameter):
        action.destroy()

    def show_about(self, data=None):
        ab = Gtk.AboutDialog()
        ab.set_program_name("hv")
        ab.set_copyright("Copyright \xc2\xa9 2017-? Marcin Bielewicz")
        ab.set_authors(["Marcin Bielewicz"])
        ab.set_website("https://github.com/lvajxi03/hv")
        ab.set_website_label("hv website")
        ab.set_title("About hv")
        ab.connect("response", self.about_onclose)
        ab.show()

    def show_editors(self, data=None):
        e_window = HEditors(self)
        e_window.set_editors(self.editors)
        response = e_window.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.editors = e_window.get_editors()
            self.update_editors()
        e_window.destroy()

    def click_flip_horiz(self, data=None):
        self.flip_horiz()

    def click_flip_vert(self, data=None):
        self.flip_vert()

    def click_rotate_cl(self, data=None):
        self.rotate_left()

    def click_rotate_cc(self, data=None):
        self.rotate_right()

    def create_ui(self, startupobj=""):

        self.imagemenu = Gtk.Menu()
        menu_item = Gtk.MenuItem("Flip _horizontally")
        menu_item.set_property('use-underline', True)
        menu_item.connect('activate', self.click_flip_horiz)
        self.imagemenu.append(menu_item)
        menu_item = Gtk.MenuItem("Flip _vertically")
        menu_item.set_property('use-underline', True)
        menu_item.connect('activate', self.click_flip_vert)
        self.imagemenu.append(menu_item)
        menu_item = Gtk.MenuItem("Rotate _clockwise")
        menu_item.set_property('use-underline', True)
        menu_item.connect('activate', self.click_rotate_cl)
        self.imagemenu.append(menu_item)
        menu_item = Gtk.MenuItem("Rotate c_ounter-clockwise")
        menu_item.set_property('use-underline', True)
        menu_item.connect('activate', self.click_rotate_cc)
        self.imagemenu.append(menu_item)
        self.imagemenu.append(Gtk.SeparatorMenuItem())
        menu_item = Gtk.MenuItem("Open _with...")
        menu_item.set_property('use-underline', True)
        self.editors_submenu = Gtk.Menu()
        menu_item.set_submenu(self.editors_submenu)
        self.imagemenu.append(menu_item)

        menu_bar = Gtk.MenuBar()
        menu_item = Gtk.MenuItem("h_v")
        menu_item.set_property('use-underline', True)
        menu = Gtk.Menu()
        menu_item.set_submenu(menu)
        menu_subitem = Gtk.MenuItem("_Preferences")
        menu_subitem.set_property('use-underline', True)
        menu_subitem.connect('activate', self.show_settings)
        menu.append(menu_subitem)
        menu_subitem = Gtk.MenuItem("_Editors")
        menu_subitem.set_property('use-underline', True)
        menu_subitem.connect('activate', self.show_editors)
        menu.append(menu_subitem)
        menu_subitem = Gtk.MenuItem("_Quit")
        menu_subitem.set_property('use-underline', True)
        menu_subitem.connect('activate', self.quit)
        menu.append(menu_subitem)
        menu_bar.append(menu_item)
        menu_item = Gtk.MenuItem("_Help")
        menu_item.set_property('use-underline', True)
        menu = Gtk.Menu()
        menu_subitem = Gtk.MenuItem("_About")
        menu_subitem.set_property('use-underline', True)
        menu_subitem.connect('activate', self.show_about)
        menu.append(menu_subitem)
        menu_item.set_submenu(menu)
        menu_bar.append(menu_item)
        stock_hi = Gtk.Image()
        self.drive_icon = stock_hi.render_icon(
            Gtk.STOCK_HARDDISK,
            Gtk.IconSize.MENU
        )
        stock_di = Gtk.Image()
        self.dir_icon = stock_di.render_icon(
            Gtk.STOCK_DIRECTORY,
            Gtk.IconSize.MENU)
        dcolumn = Gtk.TreeViewColumn("Directory name")
        dtext_renderer = Gtk.CellRendererText()
        dicon_renderer = Gtk.CellRendererPixbuf()
        dcolumn.pack_start(dicon_renderer, False)
        dcolumn.pack_start(dtext_renderer, False)
        dcolumn.set_attributes(dtext_renderer, text=1)
        dcolumn.set_attributes(dicon_renderer, pixbuf=0)

        self.file_icon = stock_di.render_icon(
            Gtk.STOCK_FILE,
            Gtk.IconSize.MENU)

        self.sv1 = Gtk.ScrolledWindow()
        self.sv1.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)

        sv2 = Gtk.ScrolledWindow()
        sv2.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)

        self.dirmodel = Gtk.ListStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING)
        self.filemodel = Gtk.ListStore(
            GdkPixbuf.Pixbuf,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING)

        fcolumn = Gtk.TreeViewColumn("Filename")
        ftext_renderer = Gtk.CellRendererText()
        ficon_renderer = Gtk.CellRendererPixbuf()
        fcolumn.pack_start(ficon_renderer, False)
        fcolumn.pack_start(ftext_renderer, False)
        fcolumn.set_attributes(ftext_renderer, text=1)
        fcolumn.set_attributes(ficon_renderer, pixbuf=0)

        fcolumn2 = Gtk.TreeViewColumn("Size")
        ftext_renderer2 = Gtk.CellRendererText()
        fcolumn2.pack_start(ftext_renderer2, False)
        fcolumn2.set_attributes(ftext_renderer2, text=3)
        fcolumn3 = Gtk.TreeViewColumn("Last modified")
        ftext_renderer3 = Gtk.CellRendererText()
        fcolumn3.pack_start(ftext_renderer3, False)
        fcolumn3.set_attributes(ftext_renderer3, text=2)

        self.dirlist = Gtk.TreeView(self.dirmodel)
        self.dirlist.append_column(dcolumn)
        self.dirlist.connect('row-activated', self.dir_activated, None)

        self.filelist = Gtk.TreeView(self.filemodel)
        self.filelist.append_column(fcolumn)
        self.filelist.append_column(fcolumn2)
        self.filelist.append_column(fcolumn3)
        self.filelist.connect('row-activated', self.file_activated, None)

        dirsel = self.dirlist.get_selection()
        dirsel.set_mode(Gtk.SelectionMode.SINGLE)
        filesel = self.filelist.get_selection()
        filesel.set_mode(Gtk.SelectionMode.SINGLE)
        filesel.connect('changed', self.file_changed)

        self.sv1.add_with_viewport(self.dirlist)
        sv2.add_with_viewport(self.filelist)

        self.statusbar = Gtk.Statusbar()
        self.context_id = self.statusbar.get_context_id("hv-context")
        self.statusbar.push(self.context_id, "/hv/")

        hpaned = Gtk.HPaned()
        hpaned.set_wide_handle(True)
        hpaned.set_position(150)
        vpaned = Gtk.VPaned()
        vpaned.set_wide_handle(True)
        vpaned.set_position(150)

        vpaned.add1(self.sv1)
        vpaned.add2(sv2)

        hpaned.add1(vpaned)
        self.sv3 = Gtk.ScrolledWindow()
        self.sv3.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.evb = Gtk.EventBox()
        self.image = Gtk.Image()
        self.evb.add(self.image)
        self.sv3.add_with_viewport(self.evb)
        hpaned.add2(self.sv3)

        self.evb.connect(
            'button-press-event',
            self.popup_image,
            self.imagemenu)

        vbox = Gtk.VBox(False, 2)
        vbox.pack_start(menu_bar, False, False, 0)
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
        self.connect('size-allocate', self.display)
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
        Gtk.main()
    except KeyboardInterrupt:
        print("Bye!")
