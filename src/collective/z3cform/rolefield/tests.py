# -*- coding: utf8 -*-

import unittest2 as unittest

from zope.interface import Invalid

from plone.app.testing.helpers import setRoles

from ecreall.helpers.testing.base import BaseTest

from collective.z3cform.rolefield.testing import ROLEFIELD_PROFILE_FUNCTIONAL
from collective.z3cform.rolefield.field import LocalRolesToPrincipalsDataManager


class TestRoleField(unittest.TestCase, BaseTest):
    """Tests adapters"""

    layer = ROLEFIELD_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestRoleField, self).setUp()
        self.portal = self.layer['portal']

    def _getTargetClass(self):
        from collective.z3cform.rolefield.field import LocalRolesToPrincipals
        return LocalRolesToPrincipals

    def _makeOne(self, *args, **kw):
        field = self._getTargetClass()(*args, **kw)
        # this is needed to initialize the vocabulary
        return field.bind(self.portal)

    def test_roles_to_assign_attribute(self):
        """If the field is not correctly configured, it fails upon validation."""
        field = self._makeOne()
        # the roles_to_assign attribute is required, if empty, validate fails
        self.assertEquals(field.roles_to_assign, ())
        self.assertRaises(Invalid, field.validate, [])
        # if we want to assign role but one does not exist, validate fails too
        field = self._makeOne(roles_to_assign=('Editor', 'WrongRole',))
        self.assertRaises(Invalid, field.validate, [])
        # if we have valid values, it works like a charm ;-)
        field = self._makeOne(roles_to_assign=('Editor', 'Reader',))
        field.validate([])

    def test_datamanager(self):
        """Test the local_roles assignment mechanism managed by the datamanager."""
        testingfield = self.portal.portal_types.testingtype.lookupSchema()['testingField']
        testingfield.roles_to_assign = ('Editor', 'Contributor',)
        # first create a sample object
        # make the default user a Manager
        member = self.portal.portal_membership.getAuthenticatedMember()
        setRoles(self.portal, member.getId(), ('Manager',))
        # create an object
        self.portal.invokeFactory('testingtype', id='testingobj')
        testingobj = getattr(self.portal, 'testingobj')
        datamanager = LocalRolesToPrincipalsDataManager(testingobj, testingfield)
        self.failIf('Administrators' in testingobj.__ac_local_roles__.keys())
        datamanager.set(('Administrators',))
        # now we have local_roles for 'Administrators'
        self.failUnless('Administrators' in testingobj.__ac_local_roles__.keys())
        # moreover, local_roles for 'Administrators' are ('Editor', 'Contributor',)
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Administrators']), testingfield.roles_to_assign)
        # add a principal, test that local_roles are adapted
        self.failIf('Reviewers' in testingobj.__ac_local_roles__.keys())
        # the value is now ('Administrators', 'Reviewers',)
        datamanager.set(('Administrators', 'Reviewers',))
        self.failUnless('Reviewers' in testingobj.__ac_local_roles__.keys())
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']), testingfield.roles_to_assign)
        # remove a group, check managed roles
        # removing a group is made by passing new value where an existing group is no more present
        self.failUnless('Administrators' in testingobj.__ac_local_roles__.keys())
        datamanager.set(('Reviewers',))
        self.failIf('Administrators' in testingobj.__ac_local_roles__.keys())
        # if an external manipulation added a local_role not managed by the field, it is kept
        # add a local_role for 'Reviewers' not managed by our field
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']), testingfield.roles_to_assign)
        testingobj.manage_addLocalRoles('Reviewers', ('Reader',))
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']), testingfield.roles_to_assign + ('Reader',))
        # remove the 'Reviewers' local_roles
        datamanager.set(())
        # not managed local_roles are kepts
        self.assertEquals(tuple(testingobj.__ac_local_roles__['Reviewers']), ('Reader',))
        # add a not existing principal value, test that it is not set
        datamanager.set(('toto',))
        self.failIf('toto' in testingobj.__ac_local_roles__.keys())
