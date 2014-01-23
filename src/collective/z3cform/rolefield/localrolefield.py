# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from zope.interface import implementer

from zope.schema import List, NO_VALUE
from zope.schema.fieldproperty import FieldPropertyStoredThroughField
from zope.interface import Invalid

from Products.CMFCore.utils import getToolByName

from .interfaces import ILocalRolesToPrincipals

import logging
logger = logging.getLogger('collective.z3cform.rolefield')


@implementer(ILocalRolesToPrincipals)
class LocalRolesToPrincipals(List):
    """Field that list principals depending on a vocabulary (by default list every available groups)
       and that assign local roles defined in the roles_to_assign attribute."""

    roles_to_assign = FieldPropertyStoredThroughField(ILocalRolesToPrincipals['roles_to_assign'])

    def __init__(self, roles_to_assign=(), **kw):
        self.roles_to_assign = roles_to_assign
        super(LocalRolesToPrincipals, self).__init__(**kw)

    def validate(self, value):
        """Check that we have roles to assign, this is mendatory and
           that roles we want to assign actually exist."""
        super(LocalRolesToPrincipals, self)._validate(value)

        # the field must specify some roles to assign as this is a required value
        if not self.roles_to_assign:
            raise Invalid(u'The field is not configured correctly, roles_to_assign is required.  " \
                          "Contact system administrator!')

        # check that roles we want to assign actually exist
        portal = getSite()
        existingRoles = [role for role in portal.acl_users.portal_role_manager.listRoleIds()]
        for role_to_assign in self.roles_to_assign:
            if not role_to_assign in existingRoles:
                raise Invalid(u'The field is not configured correctly, the defined role \'%s\' does not exist.  " \
                              "Contact system administrator!' % role_to_assign)


def remove_local_roles_from_principals(context, principals, roles):
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
    portal = getSite()
    acl_users = getToolByName(portal, 'acl_users')
    principal_ids = acl_users.getUserIds() + acl_users.getGroupIds()
    for added_principal in principals:
        if not added_principal in principal_ids:
            continue
        context.manage_addLocalRoles(added_principal, roles)


def set_local_role_on_object(context, field, event):
    roles_to_assign = field.roles_to_assign
    new_value = event.new_value
    old_value = event.old_value
    if old_value is NO_VALUE or old_value is None:
        old_value = []
    remove_local_roles_from_principals(context,
                                       old_value,
                                       roles_to_assign)
    add_local_roles_to_principals(context, new_value, roles_to_assign)


import plone.supermodel.exportimport

LocalRolesToPrincipalsHandler = plone.supermodel.exportimport.BaseHandler(LocalRolesToPrincipals)
