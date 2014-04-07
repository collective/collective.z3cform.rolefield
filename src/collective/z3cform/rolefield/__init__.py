# -*- coding: utf-8 -*-
import logging
from zope.i18nmessageid import MessageFactory


logger = logging.getLogger('collective.z3cform.rolefield')

from .localrolefield import LocalRolesToPrincipals

#pep8
LocalRolesToPrincipals

_ = MessageFactory('collective.z3cform.rolefield')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
