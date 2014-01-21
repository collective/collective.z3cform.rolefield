# -*- coding: utf-8 -*-
from zope.schema.interfaces import IList
from zope.schema import Tuple, TextLine

from .statemapping import StateMapping


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


class IStatefullLocalRolesField(IList):

    state_config = StateMapping(title=u"Local role configuration per state",
                                key_type=TextLine(),
                                required=True)
