from z3c.form import field
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from esdrt.content import MessageFactory as _
from esdrt.content.subscriptions.interfaces import INotificationSubscriptions
from esdrt.content.subscriptions.interfaces import INotificationUnsubscriptions
from five import grok
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import CMFEditionsMessageFactory as _CMFE
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.app.container.interfaces import IObjectAddedEvent
from zope.browsermenu.menu import getMenu
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory


HIDDEN_ACTIONS = [
    '/content_status_history',
    '/placeful_workflow_configuration',
]


def hidden(menuitem):
    for action in HIDDEN_ACTIONS:
        if menuitem.get('action').endswith(action):
            return True
    return False


class ITableRowSchema(form.Schema):

    line_title = schema.TextLine(title=_(u'Title'), required=True)
    co2 = schema.Int(title=_(u'CO\u2082'), required=False)
    ch4 = schema.Int(title=_(u'CH\u2084'), required=False)
    n2o = schema.Int(title=_(u'N\u2082O'), required=False)
    nox = schema.Int(title=_(u'NO\u2093'), required=False)
    co = schema.Int(title=_(u'CO'), required=False)
    nmvoc = schema.Int(title=_(u'NMVOC'), required=False)
    so2 = schema.Int(title=_(u'SO\u2082'), required=False)


# Interface class; used to define content-type schema.
class IObservation(form.Schema, IImageScaleTraversable):
    """
    New review observation
    """

    text = RichText(
        title=_(u'Text'),
        description=_(u''),
        required=True,
        )

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

    form.widget(status_flag=CheckBoxFieldWidget)
    status_flag = schema.List(
        title=_(u"Status Flag"),
        value_type=schema.Choice(
            vocabulary='esdrt.content.status_flag',
            ),


    )

    form.widget(ghg_estimations=DataGridFieldFactory)
    ghg_estimations = schema.List(
        title=_(u'GHG estimates'),
        value_type=DictRow(title=u"tablerow", schema=ITableRowSchema),
        default=[
            {'line_title': 'Original estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Revised estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},
            {'line_title': 'Corrected estimate', 'co2': 0, 'ch4': 0, 'n2o': 0, 'nox': 0, 'co': 0, 'nmvoc': 0, 'so2': 0},

        ],
    )

    form.read_permission(technical_corrections='cmf.ManagePortal')
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
        values = []
        for val in self.status_flag:
            values.append(self._vocabulary_value('esdrt.content.status_flag',
            val))
        return values

    def _vocabulary_value(self, vocabulary, term):
        vocab_factory = getUtility(IVocabularyFactory, name=vocabulary)
        vocabulary = vocab_factory(self)
        value = vocabulary.getTerm(term)
        return value.title

    def get_status(self):
        return api.content.get_state(self)



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

    def get_user_name(self, userid):
        user = api.user.get(username=userid)
        return user.getProperty('fullname', userid)

    def get_menu_actions(self):
        context = aq_inner(self.context)
        menu_items = getMenu(
            'plone_contentmenu_workflow',
            context,
            self.request
            )
        return [mitem for mitem in menu_items if not hidden(mitem)]

    def get_questions(self):
        context = aq_inner(self.context)
        return IContentListing([v for v in context.values() if v.portal_type == 'Question'])

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

    def can_add_question(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add Question', self)

    def can_edit(self):
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', self)

    def subscription_options(self):
        actions = []
        # actions.append(
        #     dict(
        #         url='/addsubscription',
        #         name=_(u'Add Subscription')
        #     )
        # )
        # actions.append(
        #     dict(
        #         url='/deletesubscription',
        #         name=_(u'Delete Subscription')
        #     )
        # )
        url = self.context.absolute_url()
        actions.append(
            dict(
                action='%s/unsubscribenotifications' % url,
                title=_(u'Unsubscribe from notifications')
            )
        )
        actions.append(
            dict(
                action='%s/deleteunsubscribenotifications' % url,
                title=_(u'Delete unsubscription from notifications')
            )
        )

        return actions




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


class AddSubscription(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')

    def render(self):
        context = self.context
        user = api.user.get_current()
        ok = INotificationSubscriptions(context).add_notifications(user.getId())
        status = IStatusMessage(self.request)
        if ok:
            status.add(_(u'Subscription enabled'), type=u'info')
        else:
            status.add(_(u'Subscription already enabled'), type=u'info')
        return self.request.response.redirect(self.context.absolute_url())


class DeleteSubscription(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')

    def render(self):
        context = self.context
        user = api.user.get_current()
        ok = INotificationSubscriptions(context).del_notifications(user.getId())
        status = IStatusMessage(self.request)
        if ok:
            status.add(_(u'Correctly unsubscribed'), type=u'info')
        else:
            status.add(_(u'You were not subscribed'), type=u'info')
        return self.request.response.redirect(self.context.absolute_url())


class UnsubscribeNotifications(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')

    def render(self):
        context = self.context
        user = api.user.get_current()
        ok = INotificationUnsubscriptions(context).unsubscribe(user.getId())
        status = IStatusMessage(self.request)
        if ok:
            status.add(_(u'Correctly unsubscribed'), type=u'info')
        else:
            status.add(_(u'You were already unsubscribed'), type=u'info')
        return self.request.response.redirect(self.context.absolute_url())


class DeleteUnsubscribeNotifications(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')

    def render(self):
        context = self.context
        user = api.user.get_current()
        ok = INotificationUnsubscriptions(context).delete_unsubscribe(
            user.getId()
        )
        status = IStatusMessage(self.request)
        if ok:
            status.add(_(u'You will receive again notifications'),
                type=u'info')
        else:
            status.add(_(u'You were not in the unsubscription list'),
                type=u'info')
        return self.request.response.redirect(self.context.absolute_url())


class ModificationForm(dexterity.EditForm):
    grok.name('modifications')
    grok.context(IObservation)
    grok.require('cmf.ModifyPortalContent')

    def updateFields(self):
        super(ModificationForm, self).updateFields()

        user = api.user.get_current()
        roles = api.user.get_roles(username=user.getId())
        fields = []
        if 'ExpertReviewer' in roles:
            fields = [
                'text', 'country', 'status_flag',
                'year', 'crf_code', 'ghg_source_category',
                'ghg_source_sectors', 'ghg_estimations',
            ]
        elif 'LeadReviewer' in roles:
            fields = ['text', 'status_flag']
        elif 'CounterPart' in roles:
            fields = ['text', 'status_flag']

        self.fields = field.Fields(IObservation).select(*fields)
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']
        if 'status_flag' in fields:
            self.fields['status_flag'].widgetFactory = CheckBoxFieldWidget
        if 'ghg_estimations' in fields:
            self.fields['ghg_estimations'].widgetFactory = DataGridFieldFactory


@grok.subscribe(IObservation, IObjectAddedEvent)
def add_observation(context, event):
    request = getRequest()
    pps = getMultiAdapter((context, request), name='plone_portal_state')
    member = pps.member()
    member_id = member.getId()
    api.user.grant_roles(
        username=member_id,
        obj=context,
        roles=['ExpertReviewer']
    )