# -*- coding: utf-8 -*-
import unittest2 as unittest
from mock import Mock

from zope import component
from zope import schema

from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from plone import api
from plone.app.testing import login, TEST_USER_NAME, setRoles, TEST_USER_ID
from ecreall.helpers.testing.base import BaseTest

from ..statefulllocalrolesfield import (StatefullLocalRolesField,
                                        update_local_roles_based_on_fields_after_transition,
                                        update_local_roles_based_on_fields_after_edit)
from ..interfaces import IStatefullLocalRolesField
from ..testing import ROLEFIELD_PROFILE_FUNCTIONAL
from .container import ITestContainer


class TestStatefullLocalRolesToPrincipals(unittest.TestCase, BaseTest):
    """Tests adapters"""
    layer = ROLEFIELD_PROFILE_FUNCTIONAL

    def setUp(self):
        super(TestStatefullLocalRolesToPrincipals, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        api.content.get_state = Mock(return_value='private')
        component.provideHandler(update_local_roles_based_on_fields_after_transition,
                                 adapts=(ITestContainer, IAfterTransitionEvent))
        component.provideHandler(update_local_roles_based_on_fields_after_edit,
                                 adapts=(ITestContainer,
                                         IStatefullLocalRolesField,
                                         schema.interfaces.IFieldUpdatedEvent))

    def _getTargetClass(self):
        return StatefullLocalRolesField

    def _makeOne(self, *args, **kw):
        field = self._getTargetClass()(*args, **kw)
        # this is needed to initialize the vocabulary
        return field.bind(self.portal)

    def test_localroles_to_assign(self):
        self.assertRaises(ValueError, self._makeOne, {})
        field = self._makeOne({u'private': {'groups': {'suffix1': 'Reader'}}})
        field.validate([])

    def test_statefull_event_on_testingtype(self):
        logs = []

        @component.adapter(ITestContainer,
                           IStatefullLocalRolesField,
                           schema.interfaces.IFieldUpdatedEvent)
        def add_field_events(obj, field, event):
            logs.append((event, obj, field))

        component.provideHandler(add_field_events)
        self.portal.invokeFactory('testingtype', 'test')
        item = getattr(self.portal, 'test')
        self.assertEqual(logs, [])
        item.stateLocalField = ['foo']
        self.assertEqual(len(logs), 1)
        event, obj, field = logs[0]
        self.assertEqual(obj, item)
        self.assertTrue(isinstance(field, StatefullLocalRolesField))
        self.assertEqual(event.old_value, None)
        self.assertEqual(event.new_value, ['foo'])

    def test_localroles_change_on_statechange(self):
        self.portal.invokeFactory('testingtype', 'test',
                                  stateLocalField=['caveman'])
        item = getattr(self.portal, 'test')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'caveman_editor': ('Editor',),
                          'dinosaur': ('Owner', )})

        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(item, 'publish')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'caveman_owner': ('Owner', )})

        workflow.doActionFor(item, 'retract')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'caveman_editor': ('Editor', ),
                          'dinosaur': ('Owner', )})

    def test_localroles_change_on_statechange_without_values(self):
        self.portal.invokeFactory('testingtype', 'test', stateLocalField=[])
        item = getattr(self.portal, 'test')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'dinosaur': ('Owner', )})

        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(item, 'publish')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', )})

        workflow.doActionFor(item, 'retract')
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'dinosaur': ('Owner', )})

    def test_localroles_change_after_edit(self):
        self.portal.invokeFactory('testingtype', 'test',
                                  stateLocalField=[])
        item = getattr(self.portal, 'test')

        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'dinosaur': ('Owner', )})
        item.stateLocalField = ['caveman']
        self.assertEqual(dict(item.get_local_roles()),
                         {'test_user_1_': ('Owner', ),
                          'dinosaur': ('Owner', ),
                          'caveman_editor': ('Editor',)})
