# -*- coding: utf-8 -*-
from zope.schema import Dict


class StateMapping(Dict):

    def validate(self, value):
        super(Dict, self).validate(value)
        if value == {}:
            raise ValueError(u'state config should not be empty')
        # verifier structure
