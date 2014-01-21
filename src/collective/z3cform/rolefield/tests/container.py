# -*- coding: utf-8 -*-
from zope import interface
from zope.schema.fieldproperty import FieldPropertyStoredThroughField

from plone.dexterity.content import Container
from plone.supermodel import model

from ..localrolefield import LocalRolesToPrincipals
from ..statefulllocalrolesfield import StatefullLocalRolesField


class ITestContainer(model.Schema):

    testingField = LocalRolesToPrincipals(title=u'testingField',
                                          required=False,
                                          roles_to_assign=('Reader', 'Owner'))

    stateLocalField = StatefullLocalRolesField(title=u'stateLocalField',
                                               required=False,
                                               state_config={u'private':
                                                             {u'groups':
                                                              {'suffix1': 'Reader', 'suffix2': 'Editor'}}})


class TestContainer(Container):
    interface.implements(ITestContainer)

    stateLocalField = FieldPropertyStoredThroughField(ITestContainer[u'stateLocalField'])

    testingField = FieldPropertyStoredThroughField(ITestContainer[u'testingField'])
