# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from zope.component import getUtility
from zope import schema

from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI

from . import logger


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
    """
    portal = getSite()
    acl_users = getToolByName(portal, 'acl_users')
    principal_ids = acl_users.getUserIds() + acl_users.getGroupIds()
    matchings = ["%s_%s" % (bpn, suffix) for bpn in base_principal_names]
    ret = []
    for principal in principal_ids:
        if principal in matchings:
            ret.append(principal)
    return ret


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
