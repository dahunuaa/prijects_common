# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-19
#

import pycurl

try:  # py3
    import urllib.request as urllib2
    from urllib.parse import quote
    from io import StringIO, BytesIO
except ImportError:  # py2
    import urllib2
    from urllib import quote
    import StringIO


class CurlClient(object):
    """使用Curl发送请求"""

    def __init__(self):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.SSL_VERIFYHOST, False)
        self.curl.setopt(pycurl.SSL_VERIFYPEER, False)
        # 设置不输出header
        self.curl.setopt(pycurl.HEADER, False)

    def set_header(self, headers):
        self.curl.setopt(pycurl.HTTPHEADER, headers)

    def get(self, url, second=30):
        return self.post(None, url, second=second, cert=False, post=False)

    def post(self, data, url, second=30, cert=False, post=True, bytes=False):
        """使用证书"""
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.TIMEOUT, second)
        # post提交方式
        if post:
            self.curl.setopt(pycurl.POST, True)
            self.curl.setopt(pycurl.POSTFIELDS, data)
        if bytes:
            buff = BytesIO()
        else:
            buff = StringIO.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buff.write)
        self.curl.perform()
        try:
            result = buff.getvalue().decode()
        except UnicodeDecodeError:
            result = buff.getvalue()
        return result
