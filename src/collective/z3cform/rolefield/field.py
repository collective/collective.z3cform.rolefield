# -*- coding: utf-8 -*-
from zope.deferredimport import deprecated

deprecated('Please import class from collective.z3cform.rolefield.localrolefield',
           LocalRolesToPrincipals='collective.z3cform.rolefield.localrolefield:LocalRolesToPrincipals',
           LocalRolesToPrincipalsDataManager='collective.z3cform.rolefield.localrolefield:LocalRolesToPrincipalsDataManager')
