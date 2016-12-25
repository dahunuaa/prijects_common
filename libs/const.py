# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#
import sys


class Const(object):
    class ConstError(TypeError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            raise (self.StatusError, "Changing Status.%s" % key)
        else:
            self.__dict__[key] = value
            for v in value:
                self.__dict__["%s_%s" % (key, v[0].upper())] = {"value": v[1], "desc": v[2]}

    def __getattr__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            return None

    def __getitem__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            return None


sys.modules[__name__] = Const()
