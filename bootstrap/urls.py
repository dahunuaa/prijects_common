# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

from projects.apps.base.handler import APIErrorHandler
from projects.libs.autoload import generate_handler_patterns, autoload_models
from projects.libs import loglib
from projects.libs import utils
import projects.modules as project_setting


def get_components(type):
    apps = getattr(project_setting, type)

    handlers = []
    ui_modules = {}

    _handlers = []
    _admin_handlers = []
    _models = []
    logger = loglib.get_logger("bootstrap")

    for a in apps:
        try:
            app_path = "%s.apps.%s" % (project_setting.name, a)
            _handlers.append((app_path, ['handler']))
            _admin_handlers.append((app_path, ['admin']))
            _models.append((app_path, ['model']))
        except:
            logger.error("loading %s error" % app_path)

    try:
        for h in _handlers:
            generate_handler_patterns(h[0], h[1], handlers, 'api/v1.0')
        for a in _admin_handlers:
            generate_handler_patterns(a[0], a[1], handlers, 'api/v1.0/admin')
        for m in _models:
            autoload_models(m[0], m[1])
    except Exception:
        print(utils.format_error())
        logger.error(utils.format_error())

    handlers.append((r".*", APIErrorHandler))
    logger.debug(handlers)
    return (handlers, ui_modules)
