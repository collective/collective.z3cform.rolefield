# -*- coding: utf-8 -*-
from copy import deepcopy

from zope import schema
from zope.component import adapts
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form import form
from z3c.form import field
from z3c.form.term import ChoiceTermsVocabulary
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITerms
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.browser.checkbox import CheckBoxWidget

from five import grok
from plone import api
from plone.app.dexterity.browser.layout import TypeFormLayout
from plone.app.dexterity.interfaces import ITypeSchemaContext

from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from Products.CMFPlone.utils import base_hasattr

from .. import _
from ..statefulllocalrolesfield import StatefullLocalRolesField

PMF = MessageFactory('plone')


def list_2_vocabulary(elements):
    terms = []
    for item in elements:
        term = SimpleVocabulary.createTerm(item[0],
                                           item[0],
                                           item[1])
        terms.append(term)
    return SimpleVocabulary(terms)


class SuffixesVocabulary(grok.GlobalUtility):
    grok.name("collective.z3cform.rolefield.config_suffixes")
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        pass


class IStateField(Interface):
    pass


class IRoleField(Interface):
    pass


class StateField(schema.Choice):
    grok.implements(IStateField)

    def __init__(self, *args, **kwargs):
        kwargs['vocabulary'] = u''
        super(StateField, self).__init__(*args, **kwargs)

    def bind(self, object):
        return super(schema.Choice, self).bind(object)


class RoleField(schema.List):
    grok.implements(IRoleField)


@grok.adapter(IRoleField, IFormLayer)
@grok.implementer(IFieldWidget)
def role_widget(field, request):
    return FieldWidget(field, CheckBoxWidget(request))


class StateTerms(ChoiceTermsVocabulary, grok.MultiAdapter):
    grok.implements(ITerms)
    grok.adapts(Interface,
                IFormLayer,
                Interface,
                IStateField,
                IWidget)

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

        portal_type = self.form.parentForm.context
        portal_workflow = portal_type.portal_workflow
        workflow = portal_workflow.getWorkflowsFor(portal_type.__name__)[0]

        self.terms = list_2_vocabulary([(s, s) for s in workflow.states])
        field.vocabulary = self.terms


@grok.provider(IContextSourceBinder)
def plone_role_generator(context):
    portal = api.portal.getSite()
    roles = []
    filtered_roles = ['Anonymous', 'Authenticated', 'Manager', 'Member', 'Site Administrator']
    for role in portal.__ac_roles__:
        if role not in filtered_roles:
            roles.append((role, PMF(role)))

    return list_2_vocabulary(roles)


@grok.provider(IContextSourceBinder)
def config_types(context):
    return list_2_vocabulary([(u'suffixes', _(u'suffixes')),
                              (u'principals', _(u'principals'))])


class IFieldRole(Interface):
    state = StateField(title=_(u'state'), required=True)

    type = schema.Choice(title=_(u'type'),
                         source=config_types,
                         required=True)

    value = schema.TextLine(title=_(u'value'))

    roles = RoleField(title=_(u'roles'),
                      value_type=schema.Choice(source=plone_role_generator),
                      required=True)


class RoleFieldConfigurationAdapter(object):
    adapts(ITypeSchemaContext)

    def __init__(self, context):
        self.__dict__['context'] = context
        self.__dict__['fti'] = self.context.fti

    def __getattr__(self, name):
        if not base_hasattr(self.context.fti, name) or not isinstance(getattr(self.context.fti, name), dict):
            raise AttributeError
        rf_dict = getattr(self.context.fti, name)
        new_list = []
        for state in sorted(rf_dict.keys()):
            for typ in sorted(rf_dict[state].keys()):
                for value in sorted(rf_dict[state][typ].keys()):
                    new_list.append({'state': state, 'type': typ, 'value': value, 'roles': rf_dict[state][typ][value]})
        return new_list

    def __setattr__(self, name, value):
        if not value:
            return
        new_dict = {}
        for row in value:
            new_dict.update({row['state']: {row['type']: {row['value']: row['roles']}}})
        setattr(self.context.fti, name, new_dict)


class RoleFieldConfigurationForm(form.EditForm):
    template = ViewPageTemplateFile('role-config.pt')
    label = _(u'Role field configuration')
    successMessage = _(u'Role fields configurations successfully updated.')
    noChangesMessage = _(u'No changes were made.')
    buttons = deepcopy(form.EditForm.buttons)
    buttons['apply'].title = PMF(u'Save')

    def update(self):
        super(RoleFieldConfigurationForm, self).update()

    def updateWidgets(self):
        super(RoleFieldConfigurationForm, self).updateWidgets()

    def getContent(self):
        return RoleFieldConfigurationAdapter(self.context)

    @property
    def fields(self):
        fields = []
        fti_schema = self.context.fti.lookupSchema()
        for name, fti_field in fti_schema.namesAndDescriptions(all=True):
            if isinstance(fti_field, StatefullLocalRolesField):
                f = schema.List(
                    __name__=str(name),
                    title=fti_field.title,
                    description=fti_field.description,
                    value_type=DictRow(title=u"fieldconfig", schema=IFieldRole)
                )
                fields.append(f)
        fields = sorted(fields, key=lambda x: x.title)
        fields = field.Fields(*fields)

        for f in fields.values():
            f.widgetFactory = DataGridFieldFactory
        return fields


class RoleConfigurationPage(TypeFormLayout):
    form = RoleFieldConfigurationForm
    label = _(u'Role field configuration')
