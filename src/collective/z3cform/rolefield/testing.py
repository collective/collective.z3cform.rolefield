# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
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

ROLEFIELD_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(ROLEFIELD,), name="ROLEFIELD_PROFILE_FUNCTIONAL")
