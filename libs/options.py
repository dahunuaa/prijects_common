# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#


import logging
import os

from tornado.options import parse_command_line, options, define
from projects.libs import configlib

def get_base_config():
    root_path = configlib.root_path
    os.chdir(root_path+'/configs')
    cfg = configlib.Config('base.icfg')
    cfg.addNamespace(configlib)
    os.chdir(root_path)
    return cfg

def parse_config_file(path):
    """Rewrite tornado default parse_config_file.

    Parses and loads the Python config file at the given path.

    This version allow customize new options which are not defined before
    from a configuration file.
    """
    config = {}
    with open(path, 'r', encoding='utf-8') as f:
        code = compile(f.read(), path, 'exec')
        exec(code, config, config)
    # execfile(path, config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])


def parse_options():
    _root = ''
    _settings = os.path.join(_root, "settings.py")
    # _projects_configs = [os.path.join(_root, "package2.icfg"),os.path.join(_root, "package.icfg")]
    # _settings_local = os.path.join(_root, "settings_local.py")

    try:
        parse_config_file(_settings)
        # parse_projects_config_file(_projects_configs)
        logging.info("Using settings.py as default settings.")
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        logging.error("No any default settings, are you sure? Exception: %s" % e)
    '''
    try:
        parse_config_file(_settings_local)
        logging.info("Override some settings with local settings.")
    except Exception, e:
        logging.error("No local settings. Exception: %s" % e)
    '''
    parse_command_line()


config = get_base_config()