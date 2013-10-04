# -*- coding: utf-8 -*-
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface

from zope.schema.interfaces import IList
from zope.schema import List, Tuple
from zope.interface import Invalid

from z3c.form.datamanager import AttributeField

import logging
logger = logging.getLogger('collective.z3cform.rolefield')


class ILocalRolesToPrincipals(IList):
    """Field that list principals depending on a vocabulary (by default list every available groups)
       and that assign local roles defined in the roles_to_assign attribute."""

    # this attribute will contains a tuple of principal to assign when the value is set
    roles_to_assign = Tuple(
        title=u"Roles to assign",
        description=u"""\
        Roles that will be automatically assigned as local roles to selected principals.
        """,
        required=True)


@implementer(ILocalRolesToPrincipals)
class LocalRolesToPrincipals(List):
    """Field that list principals depending on a vocabulary (by default list every available groups)
       and that assign local roles defined in the roles_to_assign attribute."""

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
        existingRoles = [role for role in self.context.acl_users.portal_role_manager.listRoleIds()]
        for role_to_assign in self.roles_to_assign:
            if not role_to_assign in existingRoles:
                raise Invalid(u'The field is not configured correctly, the defined role \'%s\' does not exist.  " \
                              "Contact system administrator!' % role_to_assign)


class LocalRolesToPrincipalsDataManager(AttributeField):
    """A data manager which set local roles when saving the field."""
    adapts(Interface, ILocalRolesToPrincipals)

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        # set local roles before setting the value so we still have access to the old value
        roles_to_assign = self.field.roles_to_assign
        principal_ids = self.context.acl_users.getUserIds() + self.context.acl_users.getGroupIds()
        # ---1 --- first find assigned roles to remove
        # it is not that easy to remove local roles because no helper method exists for removing
        # some specific local roles, only a method for removing every local roles for a list of principals...
        old_value = self.field.get(self.context) or ()
        # now check between old_value and value (new value) what is missing
        removed_principals = set(old_value).difference(set(value))
        # remove local_roles for removed_principals
        for local_role in self.context.get_local_roles():
            # a local_role is like ('Administrators', (u'Contributor', u'Reviewer'))
            principal = local_role[0]
            if principal in removed_principals:
                cleaned_local_roles = list(local_role[1])
                for role_to_assign in roles_to_assign:
                    try:
                        cleaned_local_roles.remove(role_to_assign)
                    except ValueError:
                        # if a role to remove was already removed (???) pass
                        logger.warn("Failed to remove role '%s' for principal '%s' on object '%s'" \
                                    % (role_to_assign, principal, '/'.join(self.context.getPhysicalPath())))
                # if there are still some local_roles, use manage_setLocalRoles
                if cleaned_local_roles:
                    self.context.manage_setLocalRoles(principal, cleaned_local_roles)
                else:
                    # either use manage_delLocalRoles
                    self.context.manage_delLocalRoles((principal,))
        # ---2 --- now add new local roles
        added_principals = set(value).difference(set(old_value))
        for added_principal in added_principals:
            if not added_principal in principal_ids:
                continue
            self.context.manage_addLocalRoles(added_principal, roles_to_assign)
        # finally set the value
        super(LocalRolesToPrincipalsDataManager, self).set(value)

import plone.supermodel.exportimport

LocalRolesToPrincipalsHandler = plone.supermodel.exportimport.BaseHandler(LocalRolesToPrincipals)
