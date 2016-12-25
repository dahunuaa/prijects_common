# -*- coding:utf-8 -*-

import projects.apps.base.model as model
from projects.libs.datatypelib import *

class AreaModel(model.StandCURDModel,model.Singleton):
    _name = "projects.area"
    _columns = [
        ("area_name",StrDT(required=True)),
        ("city_id",IDDT(table="city",required=True))
    ]




