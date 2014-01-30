# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import ploneSite
import collective.z3cform.rolefield


ROLEFIELD_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                                 package=collective.z3cform.rolefield,
                                 name='ROLEFIELD_ZCML')

ROLEFIELD_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, ROLEFIELD_ZCML),
                                     name='ROLEFIELD_Z2')

ROLEFIELD = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=collective.z3cform.rolefield,
    additional_z2_products=(),
    gs_profile_id='collective.z3cform.rolefield:testing',
    name="ROLEFIELD")


class RoleFieldFunctionalTesting(FunctionalTesting):

    def setUp(self):
        super(RoleFieldFunctionalTesting, self).setUp()
        with ploneSite() as portal:
            groups_tool = portal.portal_groups
            groups = ('caveman_editor', 'caveman_owner', 'dinosaur')
            for group_id in groups:
                if group_id not in groups_tool.getGroupIds():
                    groups_tool.addGroup(group_id)


ROLEFIELD_PROFILE_FUNCTIONAL = RoleFieldFunctionalTesting(
    bases=(ROLEFIELD, ), name="ROLEFIELD_PROFILE_FUNCTIONAL")
