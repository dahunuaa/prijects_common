# -*- coding:utf-8 -*-

import projects.apps.base.model as model
from projects.libs.datatypelib import *


class OrganizationModel(model.StandCURDModel, model.Singleton):
    _name = "projects.organization"
    _columns = [('city_id', ListIDDT(table='city')),
                ('area_id', IDDT(table='area')),
                ('status', ConstDT(const='ORDER_STATUS', required=True)),
                'remark',
                ('list', ListDT(required=True)),
                ('enable_flag', IntDT(default=1)),
                ('login_time', DatetimeDT(required=True)),
                ('mobile',MobileDT(required=True)),
                ('email',EmailDT(required=True)),
                ]
    _protect_columns = ['city_id']

