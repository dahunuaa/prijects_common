# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-09-20
#

import sys
import traceback
from tornado.web import url
from projects.libs.loglib import get_logger

logger = get_logger("bootstrap")


def generate_handler_patterns(root_module, handler_names, out_handlers, prefix=""):
    for name in handler_names:
        try:
            module_name = "%s.%s" % (root_module, name)
            __import__(module_name)
            logger.debug("Import %s success" % module_name)
            module = sys.modules[module_name]
            module_hanlders = getattr(module, "handlers", None)

            if module_hanlders:
                _handlers = []
                for handler in module_hanlders:
                    try:
                        patten = r"/%s/%s%s" % (prefix, root_module.split(".")[-1], handler[0])
                        if len(handler) == 2:
                            _handlers.append((patten,
                                              handler[1]))
                        elif len(handler) == 3:
                            _handlers.append(url(patten,
                                                 handler[1],
                                                 {"provider": handler[2]})
                                             )
                        else:
                            pass
                    except IndexError:
                        pass

                out_handlers.extend(_handlers)
            return out_handlers
        except:
            logger.error("Import %s error" % module_name)
            logger.error(traceback.format_exc())


def autoload_models(root_module, modelnames):
    for name in modelnames:
        module_name = "%s.%s" % (root_module, name)
        __import__(module_name)
        logger.debug("Import %s success" % module_name)
