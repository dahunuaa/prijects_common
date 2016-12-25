# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-05-04
#
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MODIFY_REPLACE
import traceback
import hashlib
from base64 import urlsafe_b64encode as encode
from base64 import urlsafe_b64decode as decode
import os


class LDAPUser():
    DHUI100_LDAP_HOST = 'ldap://221.226.241.34:61213'
    DHUI100_OU = "ou=donghuishangcheng,ou=shangcheng"
    LDAP_BASE_DN = 'dc=dev,dc=donghuicredit,dc=cn'
    DHUI100_LDAP_BASE_DN = '%s,%s' % (DHUI100_OU, LDAP_BASE_DN)
    LDAP_VERSION_3 = True
    LDAP_UNAME_ATTR = 'uid'
    ldapconn = None
    DEFAULT_FILTER = '(objectClass=*)'

    user = None
    password = None
    dn = None

    __ADMIN_DN = "cn=admin,dc=dev,dc=donghuicredit,dc=cn"
    __ADMIN_PASSWORD = "you123"

    def __init__(self):
        self.username = None
        self.password = None
        self.dn = None

    # 验证用户名密码
    def auth(self, username, password, dn=None):
        self.username = username
        self.password = password
        if dn is None:
            dn = '%s=%s,%s' % (self.LDAP_UNAME_ATTR, self.username, self.DHUI100_LDAP_BASE_DN)
        self.dn = dn
        return self.get_conn(dn, password)

    # 获取ldap conn
    def get_conn(self, dn=None, password=None):
        dn = self.dn if dn is None else dn
        password = self.password if password is None else password
        if dn is None or password is None:
            raise ValueError("Need auth user")
        server = Server(self.DHUI100_LDAP_HOST)
        conn = Connection(server, dn, password, auto_bind=True)
        conn.bind()
        return conn

    # 设成admin模式
    def sudo(self):
        return self.get_conn(self.__ADMIN_DN, self.__ADMIN_PASSWORD)

    # 获取当前用户的dn
    def get_dn(self):
        return self.dn

    # 列出ou下所有的
    def list(self, ou=DHUI100_OU, filter=DEFAULT_FILTER, base_dn=None, attrs=ALL_ATTRIBUTES):
        res = {}
        conn = self.get_conn()
        if self.dn != self.__ADMIN_DN:
            raise ValueError("Permission denied")
        base_dn = self.LDAP_BASE_DN if base_dn is None else base_dn
        dn = "%s,%s" % (ou, base_dn)
        res['success'] = conn.search(dn, filter, attributes=attrs)
        res['data'] = [eval(e.entry_to_json()) for e in conn.entries]
        conn.unbind()
        return res

    # 修改密码
    def change_password(self, new_password):
        res = self.update(self.username,{"userPassword":new_password})
        return res

    # 新建用户
    def create(self, username, attr):
        res = {}
        conn = self.sudo()
        dn = 'uid=%s,%s' % (username, self.DHUI100_LDAP_BASE_DN)
        res['success'] = conn.add(dn, attributes=attr)
        res['data'] = conn.result
        conn.unbind()
        return res

    # 修改用户
    def update(self, username, attr):
        res = {}
        if username != self.username and self.dn != self.__ADMIN_DN:
            raise ValueError("Permission denied")
        conn = self.sudo()
        dn = 'uid=%s,%s' % (username, self.DHUI100_LDAP_BASE_DN)
        attrs = dict([(k, [MODIFY_REPLACE, v]) for (k, v) in attr.items()])
        res['success'] = conn.modify(dn, attrs)
        res['data'] = conn.result
        conn.unbind()
        return res

    # 删除用户
    def delete(self, username):
        res = {}
        if self.dn != self.__ADMIN_DN:
            raise ValueError("Permission denied")
        conn = self.get_conn()
        dn = 'uid=%s,%s' % (username, self.DHUI100_LDAP_BASE_DN)
        res['success'] = conn.delete(dn)
        res['data'] = conn.result
        conn.unbind()
        return res

    #获取当前用户信息
    def auth_user_ldap(self):
        res = {}
        conn = self.get_conn()
        res['success'] = conn.search(self.dn, self.DEFAULT_FILTER, attributes=ALL_ATTRIBUTES)
        res['data'] = [eval(e.entry_to_json()) for e in conn.entries]
        conn.unbind()
        return res

    #加密密码
    def make_secret(self, password):
        try:  # python2
            salt = os.urandom(4)
            h = hashlib.sha1(password)
            h.update(salt)
            return "{SSHA}" + encode(h.digest() + salt)
        except:  # python3
            salt = os.urandom(4)
            h = hashlib.sha1(password.encode())
            h.update(salt)
            return "{SSHA}" + encode(h.digest() + salt).decode()

    def check_password(self, challenge_password, password):
        challenge_bytes = decode(challenge_password[6:])
        digest = challenge_bytes[:20]
        salt = challenge_bytes[20:]
        hr = hashlib.sha1(password)
        hr.update(salt)
        return digest == hr.digest()


if __name__ == '__main__':
    user = {'cn': ['donghuishangcheng'],
            'objectClass': ['posixAccount', 'top', 'inetOrgPerson'],
            'uidNumber': ['10161'],
            'title': ['test'],
            'facsimileTelephoneNumber': ['123456'],
            'postalCode': ['210000'],
            'mail': ['229465154@qq.com'],
            'postalAddress': ['qlmdj'],
            'homePostalAddress': ['hyc'],
            'loginShell': ['dhui123'],
            'gidNumber': ['0'],
            'displayName': ['wxl'],
            'pager': ['123456'],
            'homePhone': ['15077865085'],
            'telephoneNumber': ['15077865085'],
            'physicalDeliveryOfficeName': ['hyc'],
            'mobile': ['15077865085'],
            'l': ['nanjing'],
            'o': ['donghui'],
            'st': ['jiangsu'],
            'sn': ['master'],
            'homeDirectory': ['/home/shangcheng/donghuishangcheng/'],
            'givenName': ['master'],
            'initials': ['d'],
            'userPassword': []}

    update_user = {
        'homePhone': ['3333333333'],
        'telephoneNumber': ['4444444444'],
    }
    try:
        ser = LDAPUser()
        # conn,server = ser.auth("master","dhui123")
        conn = ser.auth("daemon3","test1234")
        # print(conn.result)
        # print(server.schema)
        # ser.auth("admin", "you123", "cn=admin,dc=dev,dc=donghuicredit,dc=cn")
        # print(ser.auth_user_ldap())
        # print(ser.list())
        print(ser.change_password('test123'))
        # user['userPassword'] = ser.make_secret("test123")
        # print(ser.create('daemon4',user))
        # print(ser.update("daemon4",update_user))
        # print(ser.delete("daemon4"))
    except Exception as e:
        print(traceback.format_exc())
