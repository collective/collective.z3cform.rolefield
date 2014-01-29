# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.schema import List
from zope.schema.fieldproperty import FieldPropertyStoredThroughField

import plone.supermodel.exportimport

from .interfaces import IStatefullLocalRolesField
from .utils import (get_field_from_schema, remove_local_roles_from_principals,
                    add_local_roles_to_principals,
                    get_suffixed_principals)


@implementer(IStatefullLocalRolesField)
class StatefullLocalRolesField(List):

    state_config = FieldPropertyStoredThroughField(IStatefullLocalRolesField['state_config'])

    def __init__(self, state_config, **kw):
        self.state_config = state_config
        super(StatefullLocalRolesField, self).__init__(**kw)


def update_local_roles_based_on_fields(context, event):
    old_state = event.old_state.getId()
    new_state = event.new_state.getId()
    statefull_localroles_fields = get_field_from_schema(context, IStatefullLocalRolesField)
    for field in statefull_localroles_fields:
        old_suffixes_roles = field.state_config.get(old_state, {})
        new_suffixes_roles = field.state_config.get(new_state, {})
        field_value = getattr(context, field.__name__)
        if field_value and new_suffixes_roles:
            for old_suffix, old_roles in old_suffixes_roles.items():
                principals = list(get_suffixed_principals(field_value, old_suffix))
                remove_local_roles_from_principals(context, principals, old_roles)
            for new_suffix, new_roles in new_suffixes_roles.items():
                principals = list(get_suffixed_principals(field_value, new_suffix))
                add_local_roles_to_principals(context, principals, new_roles)


StatefullLocalRolesFieldHandler = plone.supermodel.exportimport.BaseHandler(StatefullLocalRolesField)
