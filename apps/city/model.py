# -*- coding:utf-8 -*-

import projects.apps.base.model as model

class CityModel(model.StandCURDModel,model.Singleton):
    _name = "projects.city"
    _columns = []




