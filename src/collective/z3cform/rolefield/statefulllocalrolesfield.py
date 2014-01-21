# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.schema import List
from zope.schema.fieldproperty import FieldPropertyStoredThroughField

import plone.supermodel.exportimport

from .interfaces import IStatefullLocalRolesField


@implementer(IStatefullLocalRolesField)
class StatefullLocalRolesField(List):

    state_config = FieldPropertyStoredThroughField(IStatefullLocalRolesField['state_config'])

    def __init__(self, state_config, **kw):
        self.state_config = state_config
        super(StatefullLocalRolesField, self).__init__(**kw)


StatefullLocalRolesFieldHandler = plone.supermodel.exportimport.BaseHandler(StatefullLocalRolesField)
