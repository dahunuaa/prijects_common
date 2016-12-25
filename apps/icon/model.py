# -*- coding:utf-8 -*-

import projects.apps.base.model as model
from PIL import Image, ImageFont, ImageDraw
from projects.libs.datatypelib import *


class IconModel(model.StandCURDModel, model.Singleton):
    _name = "projects.icon"
    _columns = [
        ("name", StrDT(required=True)),
    ]

    def generate_image(self, name, color, icon_url):
        icon = Image.new("RGBA", (1024, 1024), color)
        image_draw = ImageDraw.ImageDraw(icon)

        # 字母数字
        image_size = 900
        if not utils.is_chinese(name):
            if len(name) >= 2:
                name = name[0].upper() + name[1].lower()
            else:
                name = name[0].upper()
            font = self.get_imagefont(800, 'en')
            image_size = image_draw.textsize(text=name, fill="white", font=font)
            x = (1024 - image_size[0]) / 2
            image_draw.text((x, 0), text=name, fill="white", font=font)
        # 中文
        else:
            name = name[:1]
            font = self.get_imagefont(800, 'cn')
            image_size = image_draw.textsize(text=name, fill="white", font=font)
            x = (1024 - image_size[0]) / 2
            image_draw.text((x, 0), text=name, fill="white", font=font)

        del image_draw
        icon.save(icon_url)

    def get_imagefont(self, font_size, language="cn"):
        if language == 'cn':
            return ImageFont.truetype(self.config("path.assets") + "/fonts/TXMH.TTF", font_size)
        else:
            return ImageFont.truetype(self.config("path.assets") + "/fonts/AGENCYB.TTF", font_size)

    def generate_icon(self):
        try:
            name = self.get_argument("name")
            colors = {
                "blue": "#1b9dff",
                "yellow": "#ffa620",
                "red": "#d20a0a",
                "transparent": None
            }

            icon_path = self.config("path.icon") + "/%s" % utils.get_current_time('directory_date')
            utils.mkdir(icon_path)
            res = {}
            for (color, value) in colors.items():
                icon_uri = "/%s" % utils.get_current_time('directory_date') + "/%s_%s.png" % (utils.get_uuid(), color)
                icon_url = self.config("path.icon") + icon_uri
                self.generate_image(name, value, icon_url)
                res[color] = self.config('domain_url') + self.config('path.icon_uri') + icon_uri
        except Exception as e:
            print(e)
            res = ""
        return res

    def before_create(self, object):
        name = self.get_argument("name")
        add_user_id = self.get_argument("add_user_id")
        icon_coll = self.coll.find_one({"name": name, "add_user_id": add_user_id})
        if icon_coll is not None:
            return icon_coll
        object['icon_url'] = self.generate_icon()
        return object
