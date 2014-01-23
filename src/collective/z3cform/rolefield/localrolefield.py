# -*- coding: utf-8 -*-
from zope.component.hooks import getSite
from zope.interface import implementer

from zope.schema import List
from zope.schema.fieldproperty import FieldPropertyStoredThroughField
from zope.interface import Invalid

from .interfaces import ILocalRolesToPrincipals
from .utils import reset_local_role_on_object


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


def set_local_role_on_object(context, field, event):
    roles_to_assign = field.roles_to_assign
    new_value = event.new_value
    old_value = event.old_value
    reset_local_role_on_object(context, roles_to_assign, old_value, new_value)

import plone.supermodel.exportimport

LocalRolesToPrincipalsHandler = plone.supermodel.exportimport.BaseHandler(LocalRolesToPrincipals)
