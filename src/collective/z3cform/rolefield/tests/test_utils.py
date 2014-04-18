# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope import component
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID
from Products.DCWorkflow.interfaces import IAfterTransitionEvent

from ..statefulllocalrolesfield import StatefullLocalRolesField
from ..statefulllocalrolesfield import update_local_roles_based_on_fields_after_transition
from ..interfaces import IStatefullLocalRolesField
from ..testing import ROLEFIELD_PROFILE_FUNCTIONAL
from ..utils import get_field_from_schema, get_suffixed_principals, add_fti_configuration, update_portaltype_local_roles
from container import ITestContainer
from test_statefulllocalrolesfield import stateful_config


class TestUtils(unittest.TestCase):

    layer = ROLEFIELD_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestUtils, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_get_role_field_from_dexterity_type(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        fields = list(get_field_from_schema(item, IStatefullLocalRolesField))
        self.assertEqual(len(fields), 2)
        for field in fields:
            self.assertTrue(isinstance(field, StatefullLocalRolesField))

    def test_get_suffixed_principals(self):
        groups = list(get_suffixed_principals(['caveman'], 'editor'))
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0], 'caveman_editor')
        groups = list(get_suffixed_principals(['caveman'], ''))
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0], 'caveman')

    def test_add_fti_configuration(self):
        add_fti_configuration('testingtype', 'stateLocalField', stateful_config)
        self.assertEqual(self.portal.portal_types.testingtype.stateLocalField, stateful_config)

    def test_update_portaltype_local_roles(self):
        component.provideHandler(update_local_roles_based_on_fields_after_transition,
                                 adapts=(ITestContainer, IAfterTransitionEvent))
        add_fti_configuration('testingtype', 'stateLocalField', stateful_config)
        self.portal.invokeFactory('testingtype', 'test',
                                  stateLocalField=['caveman'])
        item = getattr(self.portal, 'test')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'caveman_editor': ('Editor',),
                          'dinosaur': ('Owner', ), 't-rex_editor': ('Editor',)})
        new_config = {u'private': {u'suffixes': {'owner': ('Owner', )},
                                   u'principals': {('dinosaur', ): ('Editor', )}}}
        update_portaltype_local_roles('testingtype', stateful_config, new_config)
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'caveman_owner': ('Owner',),
                          'dinosaur': ('Editor', )})
