# -*- coding: utf-8 -*-
from zope.component import getUtility
from plone.dexterity.interfaces import IDexterityFTI


def get_field_from_schema(item, fieldInterface):
    """
    get all fields providing `fieldInterface` in a dexterity object `item`
    """
    item_schema = getUtility(IDexterityFTI,
                             name=item.portal_type).lookupSchema()
    for name, field in item_schema.namesAndDescriptions():
        if fieldInterface.providedBy(field):
            yield field
