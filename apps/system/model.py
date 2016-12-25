# -*- coding:utf-8 -*-

import projects.apps.base.model as model
import os
import base64

from projects.libs.datatypelib import *
from .libs.versionlib import Version


class SystemModel(model.StandCURDModel, model.Singleton):
    _name = "projects.system"
    _columns = [
        ("appname", StrDT(required=True)),
        ("version", StrDT(default="0.0.1")),
        ("icon_url", StrDT()),
        ("origin", StrDT(required=True)),
    ]

    def save_image(self):
        try:
            image_data = base64.b64decode(self.get_argument("icon"))
            icon_path = self.config("path.icon") + "/%s" % utils.get_current_time('directory_date')
            utils.mkdir(icon_path)
            icon_uri = "/%s" % utils.get_current_time('directory_date') + "/%s.png" % utils.get_uuid()
            icon_url = self.config("path.icon") + icon_uri
            f = open(icon_url, 'wb')
            f.write(image_data)
            f.close()
            res = self.config('domain_url') + self.config('path.icon_uri') + icon_uri
        except:
            res = ""
        return res

    def before_create(self, object):
        appname = self.get_argument("appname")
        add_user_id = self.get_argument("add_user_id")
        version = self.get_argument("version")
        origin = self.get_argument("origin")

        system = self.coll.find_one({"appname": appname})
        if system is not None and origin != 'quick':
            if system['add_user_id'] != add_user_id:
                raise ValueError(u"该app的名字已被注册")

            last_version = system['version']
            if version == self.columns['version'].default:
                ver = Version(last_version)
                new_version = ver.update()
            elif last_version == version:
                raise ValueError(u"两次传入的版本号相同")
            else:
                new_version = str(Version(version))
            system['version'] = new_version
            object = system
        elif system is not None and origin == 'quick':
            if system['add_user_id'] != add_user_id:
                new_appname = appname + '_' + add_user_id
                new_system = self.coll.find_one({"appname": new_appname})
                if new_system is None:
                    object['appname'] = new_appname
                    new_version = str(Version(version))
                else:
                    last_version = new_system['version']
                    if version == self.columns['version'].default:
                        ver = Version(last_version)
                        new_version = ver.update()
                    elif last_version == version:
                        raise ValueError(u"两次传入的版本号相同")
                    else:
                        new_version = str(Version(version))
                    new_system['version'] = new_version
                    object = new_system
        else:
            new_version = str(Version(version))
        object['icon_url'] = self.save_image()
        return object
