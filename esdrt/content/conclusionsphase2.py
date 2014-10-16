from zope.globalrequest import getRequest
from AccessControl import getSecurityManager
from esdrt.content.observation import hidden
from zope.component import getUtility
from plone import api
from zope.schema.interfaces import IVocabularyFactory
from zope.browsermenu.menu import getMenu
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from esdrt.content import MessageFactory as _
from five import grok
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from types import IntType
from zope import schema
from zope.interface import Invalid

class ITableRowSchema(form.Schema):

    line_title = schema.TextLine(title=_(u'Title'), required=True)
    co2 = schema.Int(title=_(u'CO\u2082'), required=False)
    ch4 = schema.Int(title=_(u'CH\u2084'), required=False)
    n2o = schema.Int(title=_(u'N\u2082O'), required=False)
    nox = schema.Int(title=_(u'NO\u2093'), required=False)
    co = schema.Int(title=_(u'CO'), required=False)
    nmvoc = schema.Int(title=_(u'NMVOC'), required=False)
    so2 = schema.Int(title=_(u'SO\u2082'), required=False)


class IConclusionsPhase2(form.Schema, IImageScaleTraversable):
    """
    Conclusions of the Second Phase of the Review
    """

    closing_reason = schema.Choice(
        title=_(u'Conclusion'),
        vocabulary='esdrt.content.conclusionphase2reasons',
        required=True,

    )

    text = RichText(
        title=_(u'Text'),
        required=True,
        )

    form.widget(ghg_estimations=DataGridFieldFactory)
    ghg_estimations = schema.List(
        title=_(u'GHG estimates [Gg CO2 eq.]'),
        value_type=DictRow(title=u"tablerow", schema=ITableRowSchema),
        default=[
            {'line_title': 'Original estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Technical correction proposed by  TERT', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Revised estimate by MS', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Corrected estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},

        ],
    )


@form.validator(field=IConclusionsPhase2['ghg_estimations'])
def check_ghg_estimations(value):
    for item in value:
        for val in item.values():
            if type(val) is IntType and val < 0:
                raise Invalid(u'Estimation values must be positive numbers')


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class ConclusionsPhase2(dexterity.Container):
    grok.implements(IConclusionsPhase2)

    def reason_value(self):
        return self._vocabulary_value('esdrt.content.conclusionphase2reasons',
            self.closing_reason
        )

    def _vocabulary_value(self, vocabulary, term):
        vocab_factory = getUtility(IVocabularyFactory, name=vocabulary)
        vocabulary = vocab_factory(self)
        try:
            value = vocabulary.getTerm(term)
            return value.title
        except LookupError:
            return u''

    def can_edit(self):
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', self)

    def can_delete(self):
        sm = getSecurityManager()
        return sm.checkPermission('Delete objects', self)

    def can_add_files(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add ESDRTFile', self)

    def get_actions(self):
        parent = aq_parent(self)
        request = getRequest()
        question_menu_items = getMenu(
            'plone_contentmenu_workflow',
            self,
            request
            )
        observation_menu_items = getMenu(
            'plone_contentmenu_workflow',
            parent,
            request
            )
        menu_items = question_menu_items + observation_menu_items
        return [mitem for mitem in menu_items if not hidden(mitem)]

    def get_files(self):
        items = self.values()
        mtool = api.portal.get_tool('portal_membership')
        return [item for item in items if mtool.checkPermission('View', item)]


class ConclusionsPhase2View(grok.View):
    grok.context(IConclusionsPhase2)
    grok.require('zope2.View')
    grok.name('view')

    def render(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        url = '%s#tab-conclusions-phase2' % parent.absolute_url()

        return self.request.response.redirect(url)