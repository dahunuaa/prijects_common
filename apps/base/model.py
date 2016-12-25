# -*- coding: utf-8 -*-

"""
    author : Daemon Wang
    date : 2016-10-14
"""

import projects.libs.mongolib as mongo
import projects.libs.utils as utils
import sys
import inspect
import traceback

from bson.son import SON
from projects.libs.datatypelib import StrDT, DataTypeError, DatetimeDT
from projects.libs.configlib import Config, ConfigList
from projects.libs.options import config as base_config


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class BaseModel(object):
    coll = None
    _request = None
    _arguments = {}
    _name = None

    def __init__(self):
        self._arguments = {}
        self._request = None
        self.coll = self.get_coll()

    def set_request(self, request):
        '''
        将request设置在model中
        :param request: handler中传来的Request对象
        :return:
        '''
        self._request = request
        self._arguments = {}
        for (k, v) in request.arguments.items():
            self._arguments[k] = v[0].decode("utf-8")

    def get_argument(self, key, default=None):
        return self._arguments.get(key, default)

    def set_argument(self, key, value):
        self._arguments[key] = value

    def remove_argument(self, key):
        if key in self._arguments.keys():
            del self._arguments[key]

    def coll_name(self):
        return self._name.split(".")[1]

    def db_name(self):
        return self._name.split(".")[0]

    def get_coll(self):
        coll_name = self.coll_name()
        coll = mongo.get_coll(coll_name)
        return coll

    def get_columns(self):
        columns = []
        coll = self.get_coll()
        if coll.find().count() > 0:
            document = coll.find_one()
            columns = document.keys()
        return columns

    def is_exist(self, value, column='_id', is_objectid=True):
        '''
        判断元素是否存在
        :param value: 元素内容
        :param column: 元素在集合中的栏位名
        :param is_objectid: 是否是objectid类型
        :return: 存在返回True，不存在返回False
        '''
        try:
            if is_objectid:
                items = self.get_coll().find_one({column: utils.create_objectid(value)})
            else:
                items = self.get_coll().find_one({column: value})
        except:
            return False
        return items != None

    @classmethod
    def get_model(cls, model_name):
        try:
            app_name = model_name.split(".")[0]
            model_classname = model_name.split(".")[1]
            model_name = 'projects.apps.%s.model' % (app_name)
            __import__(model_name)
            model_obj = sys.modules[model_name]
            models = inspect.getmembers(model_obj, inspect.isclass)
            for m in models:
                if m[0] == model_classname:
                    model = m[1]()
        except Exception as e:
            print("Can not get model %s" % model_name)
            print(traceback.format_exc())
            model = None
        return model


class StandCURDModel(BaseModel):
    _columns = []
    _protect_columns = []
    columns = {}
    protect_columns = []

    def __init__(self):
        self.columns = {}
        self.protect_columns = []
        self.parse_column()
        self._config = self.get_config()

        super(StandCURDModel, self).__init__()

    def dump(self, object, filter=None):
        '''
        格式化输出
        :param object:需要输出的字典或者列表或者pymongo游标
        :param filter: 需要过滤的参数
        :return: 过滤后的数组
        '''
        if filter is None:
            filter = self.protect_columns
        return utils.dump(object, filter)

    def parse_column(self):
        if len(self._columns) == 0:
            self.columns = {}
        else:
            for c in self._columns:
                if type(c) == tuple and len(c) >= 2:
                    self.columns[c[0]] = c[1]
                else:
                    self.columns[c] = StrDT()

            preset_columns = ['add_user_id', 'last_updated_user_id', 'delete_user_id', 'add_time', 'last_updated_time',
                              'system']
            for p in preset_columns:
                if p not in self.columns.keys():
                    if p.endswith("user_id") or p in ['system']:
                        self.columns[p] = StrDT()
                    elif p.endswith("time"):
                        self.columns[p] = DatetimeDT()
        if 'enable_flag' not in self._protect_columns:
            self.protect_columns = self._protect_columns + ['enable_flag']
        else:
            self.protect_columns = self._protect_columns

    def get_argument(self, key, default=None):
        if len(self._arguments) == 0:
            return self._arguments.get(key, default)
        if key in self.columns.keys():
            datatype = self.columns[key]
            if datatype.required == True:
                if key not in self._arguments:
                    raise ValueError(u"参数[%s]是必填参数" % key)
                else:
                    try:
                        return datatype.validate(self._arguments[key])
                    except DataTypeError as e:
                        raise Exception(u"参数[%s]传入错误:%s" % (key, str(e)))
            else:
                if key in self._arguments:
                    try:
                        return datatype.validate(self._arguments[key])
                    except DataTypeError as e:
                        raise Exception(u"参数[%s]传入错误:%s" % (key, str(e)))
            return self._arguments.get(key, self.columns[key].default)
        else:
            return self._arguments.get(key, default)

    def set_id(self, id):
        self.set_argument("_id", id)

    # 验证函数，做继承用
    def _validate_new(self, object):
        return object

    # 验证函数，做继承用
    def _validate_edit(self, object):
        return object

    # 获取格式化的传入参数
    def get_format_arguments(self):
        '''
        根据传入的参数进行格式化
        :return: 格式化个字典
        '''
        object = {}
        protect_columns = self.protect_columns
        for (k, v) in self._arguments.items():
            if len(self._columns) == 0:
                object[k] = v
                if "access_token" in object:
                    del object['access_token']
            else:
                if k in self.columns.keys():
                    datatype = self.columns[k]
                    if k in protect_columns:
                        raise ValueError(u"[%s]字段不允许更新" % k)
                    else:
                        try:
                            object[k] = datatype.validate(self._arguments[k])
                        except DataTypeError as e:
                            raise Exception(u"参数[%s]传入错误:%s" % (k, str(e)))
                else:
                    object[k] = v
        return object

    # 获取新建的对象
    def _new(self):
        object = {}
        if len(self._columns) == 0:
            object = self._arguments
            if "access_token" in object:
                del object['access_token']
        else:
            for c in self.columns.keys():
                object[c] = self.get_argument(c)
        if "enable_flag" not in object.keys() or object['enable_flag'] is None:
            object['enable_flag'] = 1

        object = self._validate_new(object)
        return object

    # 获取更新的对象
    def _edit(self):
        object = self.get_format_arguments()
        if '_id' not in object.keys():
            raise ValueError(u"没有传入_id")
        del object['_id']
        object = self._validate_edit(object)
        return object

    # 根据_id获取对象
    def _get_from_id(self, system=None):
        if system is None:
            system = self.get_argument("system")

        object = self.get_one(self.get_argument("_id", None), system=system)

        if object is None:
            raise ValueError(u"未找到指定的元素,id为[%s]" % self.get_argument("_id"))
        return object

    # 获取对象
    def get_one(self, value, column='_id', is_objectid=True, system=None):
        '''
        获取元素
        :param value: 元素内容
        :param column: 元素在集合中的栏位名
        :param is_objectid: 是否是objectid类型
        :return: 存在元素内容
        '''
        try:
            if is_objectid:
                query = {column: utils.create_objectid(value)}
            else:
                query = {column: value}

            if system is not None and system != '':
                query['system'] = system

            items = self.get_coll().find_one(query)
        except:
            return None
        return items

    # 生成删除的条件
    def _get_delete(self):
        raise NotImplementedError(u"未实现删除条件")

    def before_create(self, object):
        return object

    def after_create(self, object):
        return object

    def before_update(self, object):
        _object = self._get_from_id()
        _object.update(object)
        return _object

    def after_update(self, object):
        return object

    def before_delete(self, object):
        return object

    def after_delete(self, object):
        return object

    def create(self,object=None):
        if object is None:
            object = self._new()
        object = self.before_create(object)
        self.coll.save(object)
        object = self.after_create(object)
        return self.dump(object)

    def update(self,object=None):
        if object is None:
            object = self._edit()
        object = self.before_update(object)
        self.coll.save(object)
        object = self.after_update(object)
        return self.dump(object)

    def delete(self):
        object = self._get_from_id()
        object = self.before_delete(object)
        res = self.coll.remove(object)
        self.after_delete(object)
        return res

    def get(self):
        res = self.list()[0]
        if len(res) == 0:
            res = {}
        else:
            res = res[0]
        return res

    def list(self, query=None, sort=None, pager=None):
        if query is None:
            query = self.query()
        if sort is None:
            sort = self.sort()
        if pager is None:
            pager = self.pager()

        if pager['enable']:
            res = self.coll.aggregate([{"$match": query},
                                       {"$sort": sort},
                                       {"$skip": pager['skip']},
                                       {"$limit": pager['page_size']}])
        else:
            res = self.coll.aggregate([{"$match": query},
                                       {"$sort": sort}])

        res = self.dump(res)
        res = self.embed(res)
        res = self.fields(res)
        return res, pager

    # 获取批量获取的ids
    def get_ids(self):
        _ids = self.get_argument("_ids", None)
        res = []
        if _ids is not None:
            try:
                _ids = eval(_ids)
                if type(_ids) != list:
                    _ids = None
                for i in _ids:
                    try:
                        _o = utils.create_objectid(i)
                        res.append(_o)
                    except:
                        pass
            except:
                raise ValueError(u"传入的_ids[%s]格式有误" % _ids)
        return res

    def update_many(self,system=None):
        '''
        批量更新 如果传入参数有_ids则进行筛选更新操作
        :return: 'success' or Exception
        '''
        if system is None:
            system = self.get_argument("system")
        _ids = self.get_ids()
        query = self.get_excepted_list(self.get_format_arguments())

        if len(_ids) == 0:
            raise ValueError(u"没有传入批量更新的ids")
        if len(query.items()) == 0:
            raise ValueError(u"没有传入批量更新的内容")
        query = {"_id": {"$in": _ids}}
        if system is not None and system != '':
            query['system'] = system
        res = self.coll.update_many(query, {"$set": query}).raw_result
        return utils.dump(res)

    def delete_many(self,system=None):
        '''
        批量删除 如果传入参数有_ids则进行筛选删除操作，如果没有传，则根据传入的筛选参数进行筛选删除
        :return: 'success' or Exception
        '''
        if system is None:
            system = self.get_argument("system")
        _ids = self.get_ids()
        if len(_ids) == 0:
            raise ValueError(u"没有传入批量删除的ids")
        query = {"_id": {"$in": _ids}}
        if system is not None and system != '':
            query['system'] = system
        res = self.coll.remove(query)
        return res

    # 排序
    def sort(self):
        '''
        根据传入的参数s进行排序，例s=-priority,created_at
        :return: pymongo aggregate sort的SON格式的数组
        '''
        sort = []
        s = self.get_argument("s", "")
        sort_params = s.split(',')
        for _s in sort_params:
            if _s != '':
                # 逆序
                if _s.startswith('-'):
                    sort.append((_s[1:], -1))
                else:
                    sort.append((_s, 1))
        sort.append(("_id", 1))
        return SON(sort)

    # 返回指定字段
    def fields(self, object):
        '''
        根据传入的fields字段进行结果集的限制字段返回操作，例fields=_id,enable_flag
        :param object: 传入dict或者list类型的结果集
        :return: object：只返回限制字段的dict或者list
        '''
        fields = self.get_argument("fields", "")
        fields_params = fields.split(',')
        if fields == '':
            return object
        else:
            # Dict 类型
            if type(object) == dict:
                result = {}
                for k, v in object.items():
                    if k in fields_params:
                        result[k] = v
                return result
            # List类型
            elif type(object) == list:
                result = []
                for o in object:
                    if type(o) == dict:
                        _o = {}
                        for k, v in o.items():
                            if k in fields_params:
                                _o[k] = v
                        result.append(_o)
                    else:
                        result.append(o)
                return result
            else:
                return object

    # 获取筛选排除的字段列表
    def get_excepted_colums(self, new_columns=None):
        if new_columns is None or type(new_columns) != list:
            return ['s', 'fields', 'access_token', 'embed', 'page', 'page_size', '_ids', 'system']
        else:
            return new_columns

    # 获取筛选后的字段
    def get_excepted_list(self, query_dict=None):
        if query_dict is None:
            query_dict = self._arguments.copy()

        # 特殊字符，应排除筛选
        special_columns = self.get_excepted_colums()
        for s in special_columns:
            if s in query_dict.keys():
                del query_dict[s]
        return query_dict

    # 筛选
    def query(self):
        '''
        根据传入的参数进行精确、匹配、范围查询 例state^=open(匹配)&enable_flag=1（精确）&sort>=1（数字范围）&add_time@>=2016-10-08 10:00:01(时间范围)
        :return: pymongo aggregate match的对象
        '''
        result = {}
        query_dict = self.get_excepted_list()

        for k, v in query_dict.items():
            if v != '' and v != 'undefined':
                # 正则匹配
                if k.endswith('^'):
                    result[k[:-1]] = {"$regex": v}
                # 时间大于
                elif k.endswith('@>'):
                    try:
                        result[k[:-2]] = {"$gte": utils.strtodatetime(v, '%Y-%m-%d %H:%M:%S')}
                    except:
                        print("时间格式错误" "时间格式错误")
                # 时间小于
                elif k.endswith('@<'):
                    try:
                        result[k[:-2]] = {"$lte": utils.strtodatetime(v, '%Y-%m-%d %H:%M:%S')}
                    except:
                        print("时间格式错误")
                # 数字大于
                elif k.endswith('>'):
                    try:
                        result[k[:-1]] = {"$gte": float(v)}
                    except:
                        print("数字格式错误")
                # 数字小于
                elif k.endswith('<'):
                    try:
                        result[k[:-1]] = {"$lte": float(v)}
                    except:
                        print("数字格式错误")
                # _id转换
                elif k == '_id':
                    try:
                        result[k] = utils.create_objectid(v)
                    except:
                        print("_id格式错误")
                # 精确匹配
                else:
                    try:
                        result[k] = {"$in": [float(v), v]}
                    except:
                        result[k] = v
        system = self.get_argument("system", None)
        if system is not None and system != '':
            result['system'] = system
        return result

    # 关联文档
    def embed(self, object):
        '''
        根据传入参数 自动查询关联文档 例embed=user
        :param object: 基本文档
        :return: 带关联文档的文档
        '''
        embed = self.get_argument("embed", "")
        if embed == "":
            return object
        else:
            embed_params = embed.split(',')
            preset_columns = ['add_user', 'last_updated_user', 'delete_user']
            embed_id_param = {}
            for e in embed_params:
                if e in preset_columns:
                    embed_id_param[e] = "user_id"
                else:
                    embed_id_param[e] = '%s_id' % e

            # Dict 类型
            if type(object) == dict:
                _o = object.copy()
                for k, v in embed_id_param.items():
                    if k + '_id' in _o.keys():
                        embed_modelname = v.rstrip("_id")
                        embed_model = BaseModel.get_model(
                            "%s.%sModel" % (embed_modelname, embed_modelname.capitalize()))
                        if embed_model is not None:
                            embed_model.set_id(_o[k])
                            _o[k] = embed_model.get()
                return _o
            # List类型
            elif type(object) == list:
                result = []
                for o in object:
                    if type(o) == dict:
                        _o = o.copy()
                        for k, v in embed_id_param.items():
                            if k + '_id' in _o.keys():
                                embed_modelname = v.rstrip("_id")
                                embed_model = BaseModel.get_model(
                                    "%s.%sModel" % (embed_modelname, embed_modelname.capitalize()))
                                if embed_model is not None:
                                    embed_model.set_id(_o[k + '_id'])
                                    _o[k] = embed_model.get()
                        result.append(_o)
                    else:
                        result.append(o)
                return result
            else:
                return object

    # 分页相关
    def pager(self):
        '''
        返回分页相关的信息
        :return: 分页信息
        '''
        page = self.get_argument("page", None)
        page_size = self.get_argument("page_size", None)
        result = {}

        if page is None and page_size is None:
            result['enable'] = False
        else:
            res = self.coll.aggregate([{"$match": self.query()},
                                       {"$sort": self.sort()}])
            length = len(utils.dump(res))
            pager = utils.count_page(length, page, page_size)
            result.update(pager)
        return result

    # 获取本地的配置文件
    def get_config(self):
        config_list = []
        try:
            c = open(utils.get_root_path() + "/apps/%s/config.icfg" % self.coll_name())
            config = Config(c, 'utf-8')
            config.addNamespace(utils)
            config_list.append(config)
        except:
            print("模块[%s]未找到配置文件" % (self.coll_name()))

        try:
            # bc = open(utils.get_root_path()+"/configs/base.icfg")
            # base_config = Config(bc, 'utf-8')
            # base_config.addNamespace(utils)
            config_list.append(base_config)
        except:
            import traceback
            print(traceback.format_exc())
            print("模块[%s]未找到系统配置" % (self.coll_name()))

        if len(config_list) == 0:
            raise ValueError("模块[%s]未找到系统配置" % (self.coll_name()))

        return ConfigList(config_list)

    # 获取配置
    def config(self, value=None):
        if value is None:
            return {
                "model": self._config.getByPath("model"),
                "version": self._config.getByPath("version")
            }
        return self._config.getByPath(value)
