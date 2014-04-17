# -*- coding: utf-8 -*-
from zope import interface
from zope.schema.fieldproperty import FieldProperty

from plone.dexterity.content import Container
from plone.supermodel import model

from ..localrolefield import LocalRolesToPrincipals
from ..statefulllocalrolesfield import StatefullLocalRolesField


class ITestContainer(model.Schema):

    testingField = LocalRolesToPrincipals(title=u'testingField',
                                          required=False,
                                          roles_to_assign=('Reader', 'Owner'))

    stateLocalField = StatefullLocalRolesField(title=u'stateLocalField',
                                               required=False,)

    stateLocalField2 = StatefullLocalRolesField(title=u'stateLocalField2',
                                                required=False,)


class TestContainer(Container):
    interface.implements(ITestContainer)

    stateLocalField = FieldProperty(ITestContainer[u'stateLocalField'])

    stateLocalField2 = FieldProperty(ITestContainer[u'stateLocalField2'])

    testingField = FieldProperty(ITestContainer[u'testingField'])
