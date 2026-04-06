#!/usr/bin/env python3

"""
Config module for hv
"""


import os
import tomllib
import tomli_w


def saveconfig(configuration: dict):
    """
    Save the configuration to a file
    :param configuration: program configuration
    """
    try:
        with open(os.path.join(os.path.expanduser("~"), ".hvrc"), "wb") as fh:
            tomli_w.dump(configuration, fh)
    except IOError:
        pass
    except OSError:
        pass


def readconfig() -> dict:
    """
    Read configuration from a file
    :return: program configuration
    """
    configuration = {}
    try:
        with open(os.path.join(os.path.expanduser("~"), ".hvrc"), "rb") as f:
            configuration = tomllib.load(f)
    except IOError:
        pass
    except OSError:
        pass

    # Saturday night specials:
    if 'settings' in configuration:
        for key in ['centered', 'aspect', 'zoom', 'shrink', 'usemask']:
            try:
                if configuration['settings'][key] == 'True':
                    configuration['settings'][key] = True
                elif configuration['settings'][key] == '1':
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
