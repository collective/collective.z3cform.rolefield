# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ..statefulllocalrolesfield import StatefullLocalRolesField
from ..interfaces import IStatefullLocalRolesField
from ..testing import ROLEFIELD_PROFILE_FUNCTIONAL
from ..utils import get_field_from_schema, get_suffixed_principals, add_fti_configuration
from test_statefulllocalrolesfield import stateful_config


class TestGetFieldFromSchema(unittest.TestCase):

    layer = ROLEFIELD_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestGetFieldFromSchema, self).setUp()
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

    def test_add_fti_configuration(self):
        add_fti_configuration('testingtype', 'stateLocalField', stateful_config)
        self.assertEqual(self.portal.portal_types.testingtype.stateLocalField, stateful_config)
