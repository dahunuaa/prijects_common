# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

import os
import random
import time
import datetime
import json
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
import traceback
import string
import hashlib
import urllib
import cgi
import math
import redis
from concurrent import futures
import zipfile
import re
import projects
from projects.libs.options import config
import uuid


def get_root_path():
    return os.path.dirname(os.path.abspath(projects.__file__))

def find_modules(modules_dir):
    try:
        return [f[:-3] for f in os.listdir(modules_dir)
                if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []


def get_random_num(length, mode='string'):
    if mode == 'string':
        return ''.join([(string.ascii_letters + string.digits)[x] for x in random.sample(range(0, 62), length)])
    elif mode == 'number':
        return ''.join([(string.digits)[x] for x in random.sample(range(0, 10), length)])


def md5(str):
    m = hashlib.md5()
    m.update(str.encode())
    return m.hexdigest()

def get_uuid():
    return uuid.uuid1()

def get_current_time(format_type='datetime'):
    if format_type == 'datetime':
        format = '%Y-%m-%d %H:%M:%S'
    elif format_type == 'date':
        format = '%Y-%m-%d'
    elif format_type == 'datetime2':
        format = '%Y-%m-%d %H:%M:%S.%f'
        return datetime.datetime.now().strftime(format)[:-3]
    elif format_type == 'directory_date':
        format = '%Y/%m/%d'
    return datetime.datetime.now().strftime(format)


def timestamp_datetime(value, format_type='datetime'):
    if format_type == 'datetime':
        format = '%Y-%m-%d %H:%M:%S'
    elif format_type == 'date':
        format = '%Y-%m-%d'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = value + 8 * 60 * 60
    value = time.localtime(value)
    ## 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt


def datetime_timestamp(dt):
    # dt为字符串
    # 中间过程，一般都需要将字符串转化为时间数组
    try:
        time.strptime(dt, '%Y-%m-%d %H:%M:%S')
        ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=-1)
        # 将"2012-03-28 06:53:40"转化为时间戳
        s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
    except ValueError:
        time.strptime(dt, '%Y-%m-%d')
        ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=-1)
        # 将"2012-03-28 06:53:40"转化为时间戳
        s = time.mktime(time.strptime(dt, '%Y-%m-%d'))
    return int(s)


# 时间字符串转datetime
def strtodatetime(datestr, format):
    return datetime.datetime.strptime(datestr, format)


# 获取本地时间戳
def get_local_timestamp(type='sec'):
    return int(time.time())


# 获取当前utc时间
def get_utc_now():
    return datetime.datetime.utcnow()


# 获取当前时间
def get_now():
    return datetime.datetime.now()


# 生成objectid
def create_objectid(str=None):
    try:
        object_id = ObjectId(str)
    except:
        object_id = ''
    return object_id


# 将objectid 转换为string字符串
def objectid_str(objectid):
    return json.loads(dumps(objectid))['$oid']


# 格式化错误信息
def format_error():
    return traceback.format_exc()


# URL字符串格式解码
def urldecode(query):
    def str_format(string):
        return urllib.unquote(string).decode("utf-8")

    d = {}
    a = query.split('&')
    for s in a:
        if s.find('='):
            k, v = map(str_format, s.split('='))
            try:
                d[k].append(v)
            except KeyError:
                d[k] = v
    return d


def str_md5_hex(val):
    return hashlib.md5(val).hexdigest()


def html_encode(str):
    return cgi.escape(str)


# 计算分页信息
def count_page(length, page, page_size=15, page_show=10):
    if page is None:
        page = 1
    if page_size is None:
        page_size = 15

    page = int(page)
    page_size = int(page_size)
    length = int(length)
    if length == 0:
        return {"enable": False,
                "page_size": page_size,
                "skip": 0}
    max_page = int(math.ceil(float(length) / page_size))
    page_num = int(math.ceil(float(page) / page_show))
    pages = list(range(1, max_page + 1)[((page_num - 1) * page_show):(page_num * page_show)])
    skip = (page - 1) * page_size
    if page >= max_page:
        has_more = False
    else:
        has_more = True
    pager = {
        "page_size": page_size,
        "max_page": max_page,
        "pages": pages,
        "page_num": page_num,
        "skip": skip,
        "page": page,
        "enable": True,
        "has_more": has_more
    }
    return pager


# 将两个list合成字典
def list_to_dict(list1, list2):
    return dict(zip(list1[::], list2))


# 获取请求Host
def get_request_host(request):
    return request.headers.get_list('HOST')[0]


def zip_folder(foldername, zip_name):
    filelist = []
    if os.path.isfile(foldername):
        filelist.append(foldername)
    else:
        for root, dirs, files in os.walk(foldername):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zip_name, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(foldername):]
        # print arcname
        zf.write(tar, arcname)
    zf.close()


def get_concurrent_pool():
    return futures.ThreadPoolExecutor(4)


# def MongoDB():
#     # 建立连接
#     client = pymongo.MongoClient(config.li.mongo["host"], options.mongo["port"])
#     db = client[options.mongo["database"]]
#     if options.mongo_auth:
#         db.authenticate(options.mongo["user"], options.mongo["password"])
#     return db
#
#
# def Redis():
#     pool = redis.ConnectionPool(host=options.redis['host'],
#                                 port=options.redis['port'],
#                                 db=options.redis['db'])
#     db = redis.StrictRedis(connection_pool=pool)
#     return db


def init_response_data():
    result = {"success": 1, "return_code": "success", "error_msg": "", "data": {}}
    return result


def reset_response_data(code, e=None):
    print(format_error())
    result = init_response_data()
    if code == 1:
        result["return_code"] = "success"
    elif code == -1:
        result["return_code"] = "token invalidate"
    else:
        result["return_code"] = e or "error"
    result["success"] = code
    result["error_msg"] = format_error()

    return result


def dump(str, filter=[]):
    result = None
    if isinstance(str, pymongo.cursor.Cursor) or isinstance(str, list) or isinstance(str,
                                                                                     pymongo.command_cursor.CommandCursor):
        result = []
        for _s in str:
            if type(_s) == type({}):
                s = {}
                for (k, v) in _s.items():
                    if k in filter:
                        pass
                    elif type(v) == type(ObjectId()):
                        s[k] = json.loads(dumps(v))['$oid']
                    elif type(v) == type(datetime.datetime.utcnow()):
                        s[k] = v.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    else:
                        s[k] = v
            else:
                s = _s
            result.append(s)
    elif isinstance(str, dict):
        result = {}
        for (k, v) in str.items():
            if k in filter:
                pass
            elif type(v) == type(ObjectId()):
                result[k] = json.loads(dumps(v))['$oid']
            elif type(v) == type(datetime.datetime.utcnow()):
                result[k] = v.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            else:
                result[k] = v
    elif str is None:
        result = None
    elif len(str) == 0:
        result = str
    return result


def check_code(checkcode_coll, str, code, type="mobile"):
    # 测试用验证码 888888
    if code == "888888":
        return
    if type == "mobile":
        checkcode = checkcode_coll.find_one({"mobile": str, "enable_flag": True})
        # 验证码的有效时间
        if checkcode:
            if code.upper() != checkcode["code"].upper():
                raise Exception("填写验证码有误")
            elif checkcode["add_time"] <= datetime.datetime.now() - datetime.timedelta(minutes=10):
                raise Exception("手机验证码过期！")
            checkcode["enable_flag"] = False
            checkcode_coll.save(checkcode)
        else:
            raise Exception("获取手机验证码失败")
    elif type == "email":
        checkcode = checkcode_coll.find_one({"email": str, "enable_flag": True})
        if checkcode:
            if code.upper() != checkcode["code"].upper():
                raise Exception("填写验证码有误！")
            elif checkcode["add_time"] <= datetime.datetime.now() - datetime.timedelta(hours=30):
                raise Exception("邮箱验证码过期！")
            checkcode["enable_flag"] = False
            checkcode_coll.save(checkcode)
        else:
            raise Exception("获取邮箱验证码失败")
    else:
        raise Exception("验证码类型错误！")


# 创建目录
def mkdir(path):
    path = path.strip()
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    else:
        pass
    return path


def save_file(path, file_name, data):
    if data == None:
        return
    mkdir(path)
    if (not path.endswith("/")):
        path = path + "/"
    file = open(path + file_name, "wb")
    file.write(data)
    file.flush()
    file.close()


def check_email(email):
    return re.match("^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email) is not None


def check_mobile(mobile):
    return re.match("^1\d{10}$", mobile) is not None

def is_chinese(string):
    pattern = re.compile(u'[\u4e00-\u9fa5]+')
    return pattern.search(string)