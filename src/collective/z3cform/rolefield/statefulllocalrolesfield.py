# -*- coding: utf-8 -*-
from zope.component import getUtility
from zope.interface import implementer
from zope.schema import List
#from zope.schema.fieldproperty import FieldPropertyStoredThroughField
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
import plone.supermodel.exportimport
from Products.CMFPlone.utils import base_hasattr

from .interfaces import IStatefullLocalRolesField
from .utils import (get_field_from_schema, remove_local_roles_from_principals,
                    add_local_roles_to_principals,
                    get_suffixed_principals, replace_state_local_roles
                    )


@implementer(IStatefullLocalRolesField)
class StatefullLocalRolesField(List):
    """
    """
# The config is now stored on the fti
#    state_config = FieldPropertyStoredThroughField(IStatefullLocalRolesField['state_config'])
#    def __init__(self, **kw):
#        self.state_config = state_config
#        super(StatefullLocalRolesField, self).__init__(**kw)


def update_local_roles_based_on_fields_after_transition(context, event):
    """
        event handler to be used on transition
    """
    old_state = event.old_state.getId()
    new_state = event.new_state.getId()
    fti = getUtility(IDexterityFTI, name=context.portal_type)
    statefull_localroles_fields = get_field_from_schema(context, IStatefullLocalRolesField)
    for field in statefull_localroles_fields:
        if not base_hasattr(fti, field.__name__):
            continue
        field_config = getattr(fti, field.__name__)
        old_state_config = field_config.get(old_state, {})
        new_state_config = field_config.get(new_state, {})
        field_value = getattr(context, field.__name__)
        replace_state_local_roles(context, field_value, old_state_config, new_state_config)


def update_local_roles_based_on_fields_after_edit(context, field, event):
    """
        event handler to be used on field edit
    """
    # Avoid to set roles during object creation. Otherwise owner role isn't set
    if len(context.creators) == 0:
        return
    fti = getUtility(IDexterityFTI, name=context.portal_type)
    if not base_hasattr(fti, field.__name__):
        return
    field_config = getattr(fti, field.__name__)
    current_state = api.content.get_state(context)
    old_value = event.old_value
    suffixes_roles = field_config.get(current_state, {}).get('suffixes', {})
    for (suffix, roles) in suffixes_roles.items():
        if old_value:
            old_s_principals = list(get_suffixed_principals(old_value, suffix))
            remove_local_roles_from_principals(context, old_s_principals, roles)

    # We have to set again roles according all fields in case a necessary role was removed
    statefull_localroles_fields = get_field_from_schema(context, IStatefullLocalRolesField)
    for field in statefull_localroles_fields:
        if not base_hasattr(fti, field.__name__):
            continue
        field_config = getattr(fti, field.__name__)
        state_config = field_config.get(current_state, {})
        field_value = getattr(context, field.__name__)
        if field_value:
            suffixes_roles = state_config.get('suffixes', {})
            for suffix, roles in suffixes_roles.items():
                principals = list(get_suffixed_principals(field_value, suffix))
                add_local_roles_to_principals(context, principals, roles)
        principals = state_config.get('principals', {})
        for principals, roles in principals.items():
            add_local_roles_to_principals(context, principals, roles)


StatefullLocalRolesFieldHandler = plone.supermodel.exportimport.BaseHandler(StatefullLocalRolesField)
