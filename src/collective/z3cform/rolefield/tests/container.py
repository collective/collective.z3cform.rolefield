# -*- coding: utf-8 -*-
from zope import interface
from zope.schema.fieldproperty import FieldProperty

from plone.dexterity.content import Container
from plone.supermodel import model

from ..localrolefield import LocalRolesToPrincipals
from ..statefulllocalrolesfield import StatefullLocalRolesField


statefull_config = {u'private': {u'suffixes': {'editor': ('Editor', )},
                                 u'principals': {('dinosaur', ): ('Owner', )}},
                    u'published': {u'suffixes': {'owner': ('Owner', )}}}


class ITestContainer(model.Schema):

    testingField = LocalRolesToPrincipals(title=u'testingField',
                                          required=False,
                                          roles_to_assign=('Reader', 'Owner'))

    stateLocalField = StatefullLocalRolesField(title=u'stateLocalField',
                                               required=False,
                                               state_config=statefull_config)


class TestContainer(Container):
    interface.implements(ITestContainer)

    stateLocalField = FieldProperty(ITestContainer[u'stateLocalField'])

    testingField = FieldProperty(ITestContainer[u'testingField'])
