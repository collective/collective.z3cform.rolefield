# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope import schema

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from plone import api
from plone.dexterity.interfaces import IDexterityFTI

from . import logger
from .interfaces import IStatefullLocalRolesField


def get_field_from_schema(item, fieldInterface):
    """
    get all fields providing `fieldInterface` in a dexterity object `item`
    """
    fti = getUtility(IDexterityFTI, name=item.portal_type)
    all_fields = schema.getFieldsInOrder(fti.lookupSchema())
    for (name, field) in all_fields:
        if fieldInterface.providedBy(field):
            yield field


def get_suffixed_principals(base_principal_names, suffix):
    """
        get principals matching each " base_principal_name _ suffix "
        in case suffix is empty, return principals
    """
    if not suffix:
        return base_principal_names
    return ["%s_%s" % (bpn, suffix) for bpn in base_principal_names]


def reset_local_role_on_object(context, roles_to_assign, old_value, new_value):
    """
        reset local roles after principals change (old_value => new_value)
    """
    if old_value is not schema.NO_VALUE and old_value is not None:
        remove_local_roles_from_principals(context,
                                           old_value,
                                           roles_to_assign)
    add_local_roles_to_principals(context, new_value, roles_to_assign)


def remove_local_roles_from_principals(context, principals, roles):
    """
        remove some local roles for a list of principals
    """
    for local_principal, local_roles in dict(context.get_local_roles()).items():
        # a local_role is like (u'Contributor', u'Reviewer'))
        if local_principal in principals:
            cleaned_local_roles = list(local_roles)
            for role_to_assign in roles:
                try:
                    cleaned_local_roles.remove(role_to_assign)
                except ValueError:
                    # if a role to remove was already removed (???) pass
                    logger.warn("Failed to remove role '%s' for principal '%s' on object '%s'"
                                % (role_to_assign, local_principal, '/'.join(context.getPhysicalPath())))
            # if there are still some local_roles, use manage_setLocalRoles
            if cleaned_local_roles:
                context.manage_setLocalRoles(local_principal, cleaned_local_roles)
            else:
                # either use manage_delLocalRoles
                context.manage_delLocalRoles((local_principal, ))


def add_local_roles_to_principals(context, principals, roles):
    """
        add some local roles for a list of principals
    """
    portal = getSite()
    acl_users = getToolByName(portal, 'acl_users')
    principal_ids = acl_users.getUserIds() + acl_users.getGroupIds()
    for added_principal in principals:
        if not added_principal in principal_ids:
            continue
        context.manage_addLocalRoles(added_principal, roles)


def add_fti_configuration(portal_type, field_name, configuration, force=False):
    """
        Add in fti a specific StatefullLocalRolesField configuration
    """
    try:
        fti = getUtility(IDexterityFTI, name=portal_type)
    except ComponentLookupError:
        return "The portal type '%s' doesn't exist" % portal_type
    fields = dict([tup for tup in schema.getFieldsInOrder(fti.lookupSchema())
                   if tup[0] == field_name])
    if field_name not in fields:
        return "The given field name '%s' isn't found in the '%s' schema" % (field_name, portal_type)
    if not IStatefullLocalRolesField.providedBy(fields[field_name]):
        return "The given field name '%s' isn't an IStatefullLocalRolesField field" % (field_name)
    if base_hasattr(fti, field_name) and not force:
        return "The configuration of field '%s' on type '%s' is already set" % (field_name, portal_type)
    setattr(fti, field_name, configuration)


def replace_state_local_roles(context, field_value, old_state_config, new_state_config):
    """
    """
    if field_value:
        old_suffixes_roles = old_state_config.get('suffixes', {})
        new_suffixes_roles = new_state_config.get('suffixes', {})
        for old_suffix, old_roles in old_suffixes_roles.items():
            s_principals = list(get_suffixed_principals(field_value, old_suffix))
            remove_local_roles_from_principals(context, s_principals, old_roles)
        for new_suffix, new_roles in new_suffixes_roles.items():
            s_principals = list(get_suffixed_principals(field_value, new_suffix))
            add_local_roles_to_principals(context, s_principals, new_roles)

    old_principals = old_state_config.get('principals', {})
    new_principals = new_state_config.get('principals', {})
    for principals, roles in old_principals.items():
        remove_local_roles_from_principals(context, principals, roles)
    for principals, roles in new_principals.items():
        add_local_roles_to_principals(context, principals, roles)


def update_portaltype_local_roles(portal_type, old_config, new_config):
    """
        update portaltype objects after config modification.
        remove local roles of all fields old configuration.
        add local roles of all fields new configuration.
    """
    portal = api.portal.getSite()
    logger.info('Objects local roles update')
    for brain in portal.portal_catalog(portal_type=portal_type):
        obj = brain.getObject()
        current_state = api.content.get_state(obj)
        old_state_config = old_config.get(current_state, {})
        new_state_config = new_config.get(current_state, {})
        statefull_localroles_fields = get_field_from_schema(obj, IStatefullLocalRolesField)
        for field in statefull_localroles_fields:
            field_value = getattr(obj, field.__name__)
            replace_state_local_roles(obj, field_value, old_state_config, new_state_config)
