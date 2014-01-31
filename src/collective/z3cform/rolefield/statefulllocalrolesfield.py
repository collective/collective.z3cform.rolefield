# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.schema import List
from zope.schema.fieldproperty import FieldPropertyStoredThroughField
from plone import api

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


def update_local_roles_based_on_fields_after_transition(context, event):
    """
        event handler to be used on transition
    """
    old_state = event.old_state.getId()
    new_state = event.new_state.getId()
    statefull_localroles_fields = get_field_from_schema(context, IStatefullLocalRolesField)
    for field in statefull_localroles_fields:
        old_state_config = field.state_config.get(old_state, {})
        new_state_config = field.state_config.get(new_state, {})
        field_value = getattr(context, field.__name__)
        if field_value:
            old_suffixes_roles = old_state_config.get('suffixes', {})
            new_suffixes_roles = new_state_config.get('suffixes', {})
            for old_suffix, old_roles in old_suffixes_roles.items():
                principals = list(get_suffixed_principals(field_value, old_suffix))
                remove_local_roles_from_principals(context, principals, old_roles)
            for new_suffix, new_roles in new_suffixes_roles.items():
                principals = list(get_suffixed_principals(field_value, new_suffix))
                add_local_roles_to_principals(context, principals, new_roles)

        old_principals = old_state_config.get('principals', {})
        new_principals = new_state_config.get('principals', {})
        for principals, roles in old_principals.items():
            remove_local_roles_from_principals(context, principals, roles)
        for principals, roles in new_principals.items():
            add_local_roles_to_principals(context, principals, roles)


def update_local_roles_based_on_fields_after_edit(context, field, event):
    """
        event handler to be used on field edit
    """
    # Avoid to set roles during object creation. Otherwise owner role isn't set
    if len(context.creators) == 0:
        return
    old_value = event.old_value
    new_value = event.new_value
    current_state = api.content.get_state(context)
    field_state_config = field.state_config.get(current_state, {})
    suffixes_roles = field_state_config.get('suffixes', {})
    if suffixes_roles:
        for (suffix, roles) in suffixes_roles.items():
            if old_value:
                old_principals = list(get_suffixed_principals(old_value, suffix))
                remove_local_roles_from_principals(context, old_principals, roles)
            if new_value:
                new_principals = list(get_suffixed_principals(new_value, suffix))
                add_local_roles_to_principals(context, new_principals, roles)


StatefullLocalRolesFieldHandler = plone.supermodel.exportimport.BaseHandler(StatefullLocalRolesField)
