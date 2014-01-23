# -*- coding: utf8 -*-

import unittest2 as unittest

from zope import component
from zope import schema
from zope.interface import Invalid

from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID

from ecreall.helpers.testing.base import BaseTest

from .container import ITestContainer
from ..testing import ROLEFIELD_PROFILE_FUNCTIONAL
from ..localrolefield import LocalRolesToPrincipals
from ..utils import (remove_local_roles_from_principals,
                     add_local_roles_to_principals)

from ..interfaces import ILocalRolesToPrincipals


class TestRoleField(unittest.TestCase, BaseTest):
    """Tests adapters"""

    layer = ROLEFIELD_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestRoleField, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def _getTargetClass(self):
        return LocalRolesToPrincipals

    def _makeOne(self, *args, **kw):
        field = self._getTargetClass()(*args, **kw)
        # this is needed to initialize the vocabulary
        return field.bind(self.portal)

    def test_roles_to_assign_attribute(self):
        """If the field is not correctly configured,
           it fails upon validation."""
        field = self._makeOne()
        # the roles_to_assign attribute is required, if empty, validate fails
        self.assertEquals(field.roles_to_assign, ())
        self.assertRaises(Invalid, field.validate, [])
        # if we want to assign role but one does not exist, validate fails too
        field = self._makeOne(roles_to_assign=('Editor', 'WrongRole'))
        self.assertRaises(Invalid, field.validate, [])
        # if we have valid values, it works like a charm ;-)
        field = self._makeOne(roles_to_assign=('Editor', 'Reader'))
        field.validate([])

    def test_events(self):
        logs = []

        @component.adapter(ITestContainer,
                           ILocalRolesToPrincipals,
                           schema.interfaces.IFieldUpdatedEvent)
        def add_field_events(obj, field, event):
            logs.append((event, obj, field))

        component.provideHandler(add_field_events)
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        self.assertEqual(logs, [])
        item.testingField = ['foo']
        self.assertEqual(len(logs), 1)
        event, obj, field = logs[0]
        self.assertEqual(obj, item)
        self.assertTrue(isinstance(field, LocalRolesToPrincipals))
        self.assertEqual(event.old_value, None)
        self.assertEqual(event.new_value, ['foo'])

    def test_remove_local_roles_from_principals(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', )})
        remove_local_roles_from_principals(item, [TEST_USER_ID], ('Owner', ))
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {})

    def test_add_local_roles_to_principals(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', )})
        add_local_roles_to_principals(item, [TEST_USER_ID], ('Editor', ))
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', 'Editor')})

    def test_add_unknown_local_roles_to_principals(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', )})
        add_local_roles_to_principals(item, [TEST_USER_ID], ('Coach', ))
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', 'Coach')})

    def test_add_local_roles_to_unkown_principals(self):
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', )})
        add_local_roles_to_principals(item, ['John'], ('Editor', ))
        local_roles = dict(item.get_local_roles())
        self.assertEqual(local_roles, {TEST_USER_ID: ('Owner', )})

    def test_removed_roles(self):
        self.portal.invokeFactory('testingtype', id='testingobj')
        item = getattr(self.portal, 'testingobj')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', )})
        item.testingField = ['Administrators', 'Reviewers']
        self.assertEqual(dict(item.get_local_roles()),
                         {'Administrators': ('Reader', 'Owner'),
                          'Reviewers': ('Reader', 'Owner'),
                          'test_user_1_': ('Owner', )})
        item.testingField = ['Administrators']
        self.assertEqual(dict(item.get_local_roles()),
                         {'Administrators': ('Reader', 'Owner'),
                          'test_user_1_': ('Owner', )})

    def test_removed_roles_with_localrole_modification(self):
        self.portal.invokeFactory('testingtype', id='testingobj')
        item = getattr(self.portal, 'testingobj')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', )})
        item.testingField = ['Administrators', 'Reviewers']
        self.assertEqual(dict(item.get_local_roles()),
                         {'Administrators': ('Reader', 'Owner'),
                          'Reviewers': ('Reader', 'Owner'),
                          'test_user_1_': ('Owner', )})
        item.manage_delLocalRoles(('Administrators', ))
        self.assertEqual(dict(item.get_local_roles()),
                         {'Reviewers': ('Reader', 'Owner'),
                          'test_user_1_': ('Owner', )})
        item.testingField = ['Administrators']
        self.assertEqual(dict(item.get_local_roles()),
                         {'Administrators': ('Reader', 'Owner'),
                          'test_user_1_': ('Owner', )})

    def test_local_roles_assignation(self):
        """Test the local_roles assignment mechanism managed by the datamanager."""
        testingfield = self.portal.portal_types.testingtype.lookupSchema()['testingField']
        self.assertEqual(testingfield.roles_to_assign, ('Reader', 'Owner'))
        # first create a sample object
        # make the default user a Manager
        member = self.portal.portal_membership.getAuthenticatedMember()
        setRoles(self.portal, member.getId(), ('Manager', ))
        # create an object
        self.portal.invokeFactory('testingtype', id='testingobj')
        testingobj = getattr(self.portal, 'testingobj')
        self.failIf('Administrators' in testingobj.__ac_local_roles__.keys())
        testingobj.testingField = ['Administrators', ]
        # now we have local_roles for 'Administrators'
        self.failUnless('Administrators' in testingobj.__ac_local_roles__.keys())
        # moreover, local_roles for 'Administrators' are ('Editor', 'Contributor')
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Administrators']),
                          testingfield.roles_to_assign)
        # add a principal, test that local_roles are adapted
        self.failIf('Reviewers' in testingobj.__ac_local_roles__.keys())
        # the value is now ('Administrators', 'Reviewers')
        testingobj.testingField = ['Administrators', 'Reviewers']
        self.failUnless('Reviewers' in testingobj.__ac_local_roles__.keys())
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']),
                          testingfield.roles_to_assign)
        # remove a group, check managed roles
        # removing a group is made by passing new value where an existing group is no more present
        self.failUnless('Administrators' in testingobj.__ac_local_roles__.keys())
        testingobj.testingField = ['Reviewers', ]
        self.failIf('Administrators' in testingobj.__ac_local_roles__.keys())
        # if an external manipulation added a local_role not managed by the field, it is kept
        # add a local_role for 'Reviewers' not managed by our field
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']),
                          testingfield.roles_to_assign)
        testingobj.manage_addLocalRoles('Reviewers', ('Contributor', ))
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']),
                          testingfield.roles_to_assign + ('Contributor', ))
        # remove the 'Reviewers' local_roles
        testingobj.testingField = []
        # not managed local_roles are kepts
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']), ('Contributor', ))
        # add a not existing principal value, test that it is not set
        testingobj.testingField = ['toto', ]
        self.failIf('toto' in testingobj.__ac_local_roles__.keys())
