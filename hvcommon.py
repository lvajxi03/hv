#!/usr/bin/env python

import os
import fnmatch
import datetime
import ConfigParser

have_windows = False

try:
    import string
    from ctypes import windll
    have_windows = True
except ImportError:
    pass

DEFAULT_MASKS = "*.jpg|*.jpeg|*.png|*.gif|*.bmp|*.tga|" + \
                "*.pcx|*.svg|*ico.|*.tiff|*.tif|*.ppm|*.pnm|*.idraw"

BACKGROUND_NONE = 0
BACKGROUND_WHITE = 1
BACKGROUND_BLACK = 2
BACKGROUND_CHECKERED = 3
BACKGROUND_CUSTOM = 4


def sizeof_fmt(num, suffix='B'):
    for unit in ['',
                 'Ki',
                 'Mi',
                 'Gi',
                 'Ti',
                 'Pi',
                 'Ei',
                 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_max_rect(w1, h1, w2, h2):
    w = w1 if w1 > w2 else w2
    h = h1 if h1 > h2 else h2
    return (w, h)


def get_location(ww, wh, pw, ph):
    x = int((ww - pw)/2)
    y = int((wh - ph)/2)
    return (x, y)


def is_bigger_than_dp(iw, ih, dw, dh):
    """Is bigger than display port

    This routine checks if an image is bigger than a display port

    Args:
        iw (int): image width
        ih (int): image height
        dw (int): display port width
        dh (int): display port height

    Returns:
        bool: True if bigger, False otherwise
    """
    if iw > dw:
        return True
    if ih > dh:
        return True
    return False


def calculate_shrink(iw, ih, dw, dh, aspect=True):
    if is_bigger_than_dp(iw, ih, dw, dh):
        if aspect:
            f1 = (iw * 1.0)/(dw * 1.0)
            f2 = (ih * 1.0)/(dh * 1.0)
            f = max(f1, f2)
            return (int((iw * 1.0)/f), int((ih * 1.0)/f))
        return (dw, dh)
    return (iw, ih)


def calculate_zoom(iw, ih, dw, dh, aspect=True):
    if is_bigger_than_dp(iw, ih, dw, dh):
        return (iw, ih)
    else:
        if aspect:
            f1 = (dw * 1.0)/(iw * 1.0)
            f2 = (dh * 1.0)/(ih * 1.0)
            f = min(f1, f2)
            return (int(iw * f), int(ih * f))
        return (dw, dh)


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
            size = sizeof_fmt(statinfo.st_size)
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


def getdirs_full(curdir="."):
    try:
        os.chdir(curdir)
        dirs = []
        for f in os.listdir(curdir):
            if os.path.isdir(f):
                dirs.append(f)
        dirs.sort()
        dirs.insert(0, '.')
        dirs.insert(0, '..')

        full = []
        for name in dirs:
            mtime = os.path.getmtime(name)
            ts = datetime.datetime.fromtimestamp(
                mtime).strftime('%Y-%m-%d %H:%M:%S')
            statinfo = os.stat(name)
            size = sizeof_fmt(statinfo.st_size)
            full.append([name, ts, size])
        return full
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
    except OSError:
        pass
    # Saturday night specials:
    if 'settings' in configuration:
        for key in ['centered', 'aspect', 'maximize', 'shrink', 'usemask']:
            try:
                if configuration['settings'][key] == 'True':
                    configuration['settings'][key] = True
                else:
                    configuration['settings'][key] = False
            except KeyError:
                configuration['settings'][key] = False
    editors = []
    if 'editors' in configuration:
        for i in range(10):
            try:
                name = configuration['editors']['name%(n)d' % {'n': i}]
                command = configuration['editors']['command%(n)d' % {'n': i}]
                if name and command:
                    editors.append((name, command))
            except KeyError:
                pass
    configuration['editors'] = editors
    return configuration


checkers = [
    "100 100 2 1",
    " 	c #FFFFFF",
    ".	c #DEDEDE",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "                                                  ..................................................",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  ",
    "..................................................                                                  "]
