from AccessControl import getSecurityManager
from Acquisition import aq_inner
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from esdrt.content import MessageFactory as _
from five import grok
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import CMFEditionsMessageFactory as _CMFE
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory


class ITableRowSchema(form.Schema):

    title = schema.TextLine(title=_(u'Title'), required=True)
    co2 = schema.TextLine(title=_(u'CO\u2082'), required=False)
    ch4 = schema.TextLine(title=_(u'CH\u2084'), required=False)
    n2o = schema.TextLine(title=_(u'N\u2082O'), required=False)
    nox = schema.TextLine(title=_(u'NO\u2093'), required=False)
    co = schema.TextLine(title=_(u'CO'), required=False)
    nmvoc = schema.TextLine(title=_(u'NMVOC'), required=False)
    so2 = schema.TextLine(title=_(u'SO\u2082'), required=False)


# Interface class; used to define content-type schema.
class IObservation(form.Schema, IImageScaleTraversable):
    """
    New review observation
    """
    country = schema.Choice(
        title=_(u"Country"),
        vocabulary='esdrt.content.eu_member_states',

    )

    year = schema.Int(
        title=_(u'Observation year'),
    )

    crf_code = schema.Choice(
        title=_(u"CRF Code"),
        vocabulary='esdrt.content.crf_code',

    )

    ghg_source_category = schema.Choice(
        title=_(u"GHG Source Category"),
        vocabulary='esdrt.content.ghg_source_category',

    )

    ghg_source_sectors = schema.Choice(
        title=_(u"GHG Source Sectors"),
        vocabulary='esdrt.content.ghg_source_sectors',

    )

    status_flag = schema.Choice(
        title=_(u"Status Flag"),
        vocabulary='esdrt.content.status_flag',

    )

    form.widget(ghg_estimations=DataGridFieldFactory)
    ghg_estimations = schema.List(
        title=_(u'GHG estimates'),
        value_type=DictRow(title=u"tablerow", schema=ITableRowSchema),
        default=[
            {'title': 'Original estimate'},
            {'title': 'Revised estimate'},
            {'title': 'Corrected estimate'},

        ],
    )

    form.write_permission(technical_corrections='cmf.ManagePortal')
    technical_corrections = RichText(
        title=_(u'Technical Corrections'),
        required=False
    )


class Observation(dexterity.Container):
    grok.implements(IObservation)
    # Add your class methods and properties here

    def country_value(self):
        return self._vocabulary_value('esdrt.content.eu_member_states',
            self.country
        )

    def crf_code_value(self):
        return self._vocabulary_value('esdrt.content.crf_code',
            self.crf_code
        )

    def ghg_source_category_value(self):
        return self._vocabulary_value('esdrt.content.ghg_source_category',
            self.ghg_source_category
        )

    def ghg_source_sectors_value(self):
        return self._vocabulary_value('esdrt.content.ghg_source_sectors',
            self.ghg_source_sectors
        )

    def status_flag_value(self):
        return self._vocabulary_value('esdrt.content.status_flag',
            self.status_flag
        )

    def _vocabulary_value(self, vocabulary, term):
        vocab_factory = getUtility(IVocabularyFactory, name=vocabulary)
        vocabulary = vocab_factory(self)
        value = vocabulary.getTerm(term)
        return value.title

# View class
# The view will automatically use a similarly named template in
# templates called observationview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type

grok.templatedir('templates')


class ObservationView(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')
    grok.name('view')

    def wf_info(self):
        context = aq_inner(self.context)
        wf = getToolByName(context, 'portal_workflow')
        comments = wf.getInfoFor(self.context,
            'comments', wf_id='esd-review-workflow')
        actor = wf.getInfoFor(self.context,
            'actor', wf_id='esd-review-workflow')
        time = wf.getInfoFor(self.context,
            'time', wf_id='esd-review-workflow')
        return {'comments': comments, 'actor': actor, 'time': time}

    def isManager(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)
        return sm.checkPermission('Manage portal', context)

    @property
    def repo_tool(self):
        return getToolByName(self.context, "portal_repository")

    def getVersion(self, version):
        context = aq_inner(self.context)
        if version == "current":
            return context
        else:
            return self.repo_tool.retrieve(context, int(version)).object

    def versionName(self, version):
        """
        Copied from @@history_view
        Translate the version name. This is needed to allow translation
        when `version` is the string 'current'.
        """
        return _CMFE(version)

    def versionTitle(self, version):
        version_name = self.versionName(version)

        return translate(
            _CMFE(u"version ${version}",
              mapping=dict(version=version_name)),
            context=self.request
        )

    # def update(self):
    #     history_metadata = self.repo_tool.getHistoryMetadata(self.context)
    #     retrieve = history_metadata.retrieve
    #     getId = history_metadata.getVersionId
    #     history = self.history = []
    #     # Count backwards from most recent to least recent
    #     for i in xrange(history_metadata.getLength(countPurged=False)-1, -1, -1):
    #         version = retrieve(i, countPurged=False)['metadata'].copy()
    #         version['version_id'] = getId(i, countPurged=False)
    #         history.append(version)
    #     dt = getToolByName(self.context, "portal_diff")

    #     version1 = self.request.get("one", None)
    #     version2 = self.request.get("two", None)

    #     if version1 is None and version2 is None:
    #         self.history.sort(lambda x,y: cmp(x.get('version_id', ''), y.get('version_id')), reverse=True)
    #         version1 = self.history[-1].get('version_id', 'current')
    #         version2 = self.history[-2].get('version_id', 'current')
    #     elif version1 is None:
    #         version1 = 'current'
    #     elif version2 is None:
    #         version2 = 'current'

    #     self.request.set('one', version1)
    #     self.request.set('two', version2)

    #     changeset = dt.createChangeSet(
    #             self.getVersion(version2),
    #             self.getVersion(version1),
    #             id1=self.versionTitle(version2),
    #             id2=self.versionTitle(version1))
    #     self.changes = [change for change in changeset.getDiffs()
    #                   if not change.same]
