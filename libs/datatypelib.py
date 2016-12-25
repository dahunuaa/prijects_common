# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-10-09
#
from . import utils
import datetime


class BaseDataTypeClass(object):
    type = None
    default = None
    required = None
    protected = None

    def __init__(self, type, required, default):
        self.required = required
        self.type = type
        self.default = default

    def validate(self, value):
        if value is None:
            value = self.default
        if type(value) != self.type:
            raise DataTypeError(u"参数传入错误，应传入[%s]类型，实际传入[%s]类型" % (str(self.type), str(type(value))))
        return value


class DataTypeError(BaseException):
    def __init__(self, *args, **kwargs):
        super(DataTypeError, self).__init__(*args, **kwargs)


class StrDT(BaseDataTypeClass):
    default = None

    def __init__(self, required=False, default=""):
        super(StrDT, self).__init__(str, required, default)

    def validate(self, value=default):
        return super(StrDT, self).validate(value)


class IntDT(BaseDataTypeClass):
    default = None

    def __init__(self, required=False, default=0):
        super(IntDT, self).__init__(int, required, default)

    def validate(self, value=default):
        try:
            value = int(value)
        except:
            raise DataTypeError(u"[%s]不是合法的整数类型" % value)
        return super(IntDT, self).validate(value)


class FloatDT(BaseDataTypeClass):
    default = None

    def __init__(self, required=False, default=0.0):
        super(FloatDT, self).__init__(float, required, default)

    def validate(self, value=default):
        try:
            value = float(value)
        except:
            raise DataTypeError(u"[%s]不是合法的浮点数类型" % value)
        return super(FloatDT, self).validate(value)


class DatetimeDT(BaseDataTypeClass):
    default = None

    def __init__(self, required=False, default=utils.get_now()):
        super(DatetimeDT, self).__init__(type(datetime.datetime.now()), required, default)

    def validate(self, value=default):
        if type(value) == str:
            try:
                value = utils.strtodatetime(value, '%Y-%m-%d %H:%M:%S')
            except:
                raise DataTypeError(u"[%s]不是合法的日期类型 例:2008-01-01 23:59:59" % value)
        return super(DatetimeDT, self).validate(value)


class ListDT(BaseDataTypeClass):
    default = None

    def __init__(self, required=False, default=[]):
        super(ListDT, self).__init__(list, required, default)

    def validate(self, value=default):
        if type(value) == str:
            try:
                value = eval(value)
            except:
                raise DataTypeError(u"[%s]不是合法的列表" % value)
        return super(ListDT, self).validate(value)


class IDDT(BaseDataTypeClass):
    table = None
    model = None
    default = None

    def __init__(self, table, model=None, required=False, default=''):
        self.required = required
        self.table = table
        self.type = str
        self.default = default

    def validate(self, value=default):
        from projects.apps.base.model import BaseModel

        if self.model is None:
            model = BaseModel.get_model("%s.%sModel" % (self.table, self.table.capitalize()))
        else:
            model = BaseModel.get_model("%s" % (self.model))

        if model is None:
            raise DataTypeError(u"模块[%s]不存在" % self.table)
        if value != self.default and not model.is_exist(value):
            raise DataTypeError(u"[%s]该元素id不存在于[%s]" % (value, self.table))
        return super(IDDT, self).validate(value)


class ListIDDT(ListDT):
    table = None
    model = None
    default = None

    def __init__(self, table, model=None, required=False, default=[]):
        self.table = table
        self.model = model
        super(ListIDDT, self).__init__(required, default)

    def validate(self, value=default):
        from projects.apps.base.model import BaseModel

        if self.model is None:
            model = BaseModel.get_model("%s.%sModel" % (self.table, self.table.capitalize()))
        else:
            model = BaseModel.get_model("%s" % (self.model))

        if type(value) == str:
            try:
                value = eval(value)
            except:
                raise DataTypeError(u"[%s]输入的格式不是列表型" % self.table)

        if self.required == True and len(value) == 0:
            raise DataTypeError(u"[%s]输入的列表内容为空" % self.table)

        for v in value:
            if model is None:
                raise DataTypeError(u"模块[%s]不存在" % self.table)
            if not model.is_exist(v):
                raise DataTypeError(u"[%s]该元素id不存在于[%s]" % (value, self.table))
        return super(ListDT, self).validate(value)


class ConstDT(BaseDataTypeClass):
    const = None
    default = None

    def __init__(self, const, required=False, default=None):
        self.const = const
        super(ConstDT, self).__init__(dict, required, default)

    def validate(self, value=default):
        from projects.libs import const
        _const = const[self.const]
        res = None
        for c in _const:
            if str(value) == str(c[1]):
                res = c
                break
        if res is None:
            raise DataTypeError(u"[%s]不存在于常量[%s]中" % (value, self.const))
        value = {"value": res[1], "desc": res[2]}
        return super(ConstDT, self).validate(value)


class EmailDT(StrDT):
    default = None

    def validate(self, value=default):
        if not utils.check_email(value):
            raise DataTypeError(u"[%s]不是合法的邮件格式" % (value))
        return super(EmailDT, self).validate(value)


class MobileDT(StrDT):
    default = None

    def validate(self, value=default):
        if not utils.check_mobile(value):
            raise DataTypeError(u"[%s]不是合法的手机格式" % (value))
        return super(MobileDT, self).validate(value)
