#!/usr/bin/env python

"""
hv Utility module
"""


import os
import fnmatch
import datetime


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
BACKGROUND_GRID = 4


def sizeof_fmt(num, suffix='B') -> str:
    """
    Format file size in Ki(B)s, Mi(B)s, etc
    :param num: numeric size value
    :param suffix: custom suffix (default: B)
    :return: formatted size (str)
    """
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


def get_max_rect(w1, h1, w2, h2) -> tuple:
    """
    Calculate maximum rectangle of two given heights and widths
    :param w1: first width
    :param w2: second width
    :param h1: first height
    :param h2: second height
    :return: maximal rectangle size (tuple of width and height)
    """
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
    """
    Calculate shrink factors
    :param iw: image width
    :param ih: image height
    :param dw: display width
    :param dh: display height
    :param aspect: whether to keep the aspect ratio
    :return new shrink (width, height)
    """
    if is_bigger_than_dp(iw, ih, dw, dh):
        if aspect:
            f1 = (iw * 1.0)/(dw * 1.0)
            f2 = (ih * 1.0)/(dh * 1.0)
            f = max(f1, f2)
            return (int((iw * 1.0)/f), int((ih * 1.0)/f))
        return (dw, dh)
    return (iw, ih)


def calculate_zoom(iw, ih, dw, dh, aspect=True):
    """
    Calculate zoom factors
    :param iw: image width
    :param ih: image height
    :param dw: display width
    :param dh: display height
    :param aspect: whether to keep the aspect ratio
    :return: new zoom (width, height)
    """
    if is_bigger_than_dp(iw, ih, dw, dh):
        return (iw, ih)
    if aspect:
        f1 = (dw * 1.0)/(iw * 1.0)
        f2 = (dh * 1.0)/(ih * 1.0)
        f = min(f1, f2)
        return (int(iw * f), int(ih * f))
    return (dw, dh)


def get_drives() -> list:
    """
    Get drives list
    :return: list of available drives in Windows
    """
    drives = []
    if have_windows:
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1
    return drives


def getfiles(curdir=".", masks: list = None):
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


def getdirs(curdir=".") -> list:
    """
    Get list of subdirectories of the given one
    :param curdir: current directory to list
    :return: list of subdirectories
    """
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


def getdirs_full(curdir=".") -> list:
    """
    Get full list of directory content
    :param curdir: current directory name
    :return: list of directory content, including
             name, modified timestamp and size
    """
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
