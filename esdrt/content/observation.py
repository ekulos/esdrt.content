from plone.z3cform.interfaces import IWrappedForm
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
from plone.app.textfield.value import RichTextValue
from plone.directives import dexterity
from plone.directives import form
from plone.directives.form import default_value
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import CMFEditionsMessageFactory as _CMFE
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from time import time
from types import IntType
from z3c.form import button
from z3c.form import field
from z3c.form import interfaces
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.form import Form
from z3c.form.interfaces import ActionExecutionError
from zope import schema
from zope.browsermenu.menu import getMenu
from zope.component import getUtility
from zope.container.interfaces import IObjectAddedEvent
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory
from .comment import IComment
from .conclusion import IConclusion

import datetime

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
        title=_(u'Short description'),
        description=_(u''),
        required=True,
        )

    country = schema.Choice(
        title=_(u"Country"),
        vocabulary='esdrt.content.eea_member_states',
        required=True,
    )

    year = schema.TextLine(
        title=_(u'Inventory year'),
        required=True
    )

    gas = schema.Choice(
        title=_(u"Gas"),
        vocabulary='esdrt.content.gas',
        required=True,
    )

    review_year = schema.Int(
        title=_(u'Review year'),
        required=True,
    )

    fuel = schema.Choice(
        title=_(u"Fuel"),
        vocabulary='esdrt.content.fuel',
        required=False,
    )

    ghg_source_category = schema.Choice(
        title=_(u"CRF category group"),
        vocabulary='esdrt.content.ghg_source_category',
        required=False,
    )

    ghg_source_sectors = schema.Choice(
        title=_(u"CRF Sector"),
        vocabulary='esdrt.content.ghg_source_sectors',
        required=True,
    )

    ms_key_catagory = schema.Bool(
        title=_(u"MS key category"),
    )

    eu_key_catagory = schema.Bool(
        title=_(u"EU key category"),
    )

    crf_code = schema.Choice(
        title=_(u"CRF category codes"),
        vocabulary='esdrt.content.crf_code',
        required=True,
    )

    form.widget(highlight=CheckBoxFieldWidget)
    highlight = schema.List(
        title=_(u"Highlight"),
        value_type=schema.Choice(
            vocabulary='esdrt.content.highlight',
            ),
        required=False,
    )

    form.widget(parameter=RadioFieldWidget)
    parameter = schema.Choice(
        title=_(u"Parameter"),
        vocabulary='esdrt.content.parameter',
        required=True,
    )

    # form.widget(status_flag=CheckBoxFieldWidget)
    # status_flag = schema.List(
    #     title=_(u"Status Flag"),
    #     value_type=schema.Choice(
    #         vocabulary='esdrt.content.status_flag',
    #         ),
    # )

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

    form.read_permission(technical_corrections='cmf.ManagePortal')
    form.write_permission(technical_corrections='cmf.ManagePortal')
    technical_corrections = RichText(
        title=_(u'Technical Corrections'),
        required=False
    )

    form.write_permission(closing_reason='cmf.ManagePortal')
    closing_reason = schema.Choice(
        title=_(u'Finish request reason'),
        vocabulary='esdrt.content.finishobservationreasons',
        required=False,

    )

    form.write_permission(closing_comments='cmf.ManagePortal')
    closing_comments = RichText(
        title=_(u'Finish request comments'),
        required=False,
    )

    form.write_permission(closing_deny_reason='cmf.ManagePortal')
    closing_deny_reason = schema.Choice(
        title=_(u'Finish deny reason'),
        vocabulary='esdrt.content.finishobservationdenyreasons',
        required=False,

    )

    form.write_permission(closing_deny_comments='cmf.ManagePortal')
    closing_deny_comments = RichText(
        title=_(u'Finish deny comments'),
        required=False,
    )


@form.validator(field=IObservation['ghg_estimations'])
def check_ghg_estimations(value):
    for item in value:
        for val in item.values():
            if type(val) is IntType and val < 0:
                raise Invalid(u'Estimation values must be positive numbers')


@form.validator(field=IObservation['ghg_source_sectors'])
def check_sector(value):
    user = api.user.get_current()
    groups = user.getGroups()
    valid = False
    for group in groups:
        if group.startswith('extranet-esd-reviewexperts-%s-' % value):
            valid = True

    if not valid:
        raise Invalid(u'You are not allowed to add observations for this sector')


@form.validator(field=IObservation['country'])
def check_country(value):
    user = api.user.get_current()
    groups = user.getGroups()
    valid = False
    for group in groups:
        if group.startswith('extranet-esd-reviewexperts-') and \
            group.endswith('-%s' % value):
            valid = True

    if not valid:
        raise Invalid(u'You are not allowed to add observations for this country')


@default_value(field=IObservation['review_year'])
def default_year(data):
    return datetime.datetime.now().year


@grok.subscribe(IObservation, IObjectAddedEvent)
@grok.subscribe(IObservation, IObjectModifiedEvent)
def add_observation(object, event):
    sector = safe_unicode(object.ghg_source_category_value())
    gas = safe_unicode(object.gas_value())
    inventory_year = safe_unicode(str(object.year))
    parameter = safe_unicode(object.parameter_value())
    object.title = u' '.join([sector, gas, inventory_year, parameter])


class Observation(dexterity.Container):
    grok.implements(IObservation)
    # Add your class methods and properties here

    def get_crf_code(self):
        """ stupid method to avoid name-clashes with the existing
        vocabularies when cataloging """
        return self.crf_code

    def get_ghg_source_sectors(self):
        """ stupid method to avoid name-clashes with the existing
        vocabularies when cataloging """
        return self.ghg_source_sectors

    def get_highlight(self):
        """ stupid method to avoid name-clashes with the existing
        vocabularies when cataloging """
        return self.highlight

    def country_value(self):
        return self._vocabulary_value('esdrt.content.eea_member_states',
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

    def parameter_value(self):
        return self._vocabulary_value('esdrt.content.parameter',
            self.parameter
        )

    def gas_value(self):
        return self._vocabulary_value('esdrt.content.gas',
            self.gas
        )

    def highlight_value(self):

        highlight = [self._vocabulary_value('esdrt.content.highlight',
            h) for h in self.highlight]
        return u', '.join(highlight)

    def status_flag_value(self):
        values = []
        for val in self.status_flag:
            values.append(self._vocabulary_value('esdrt.content.status_flag',
            val))
        return values

    def finish_reason_value(self):
        return self._vocabulary_value('esdrt.content.finishobservationreasons',
            self.closing_reason
        )

    def finish_deny_reason_value(self):
        return self._vocabulary_value('esdrt.content.finishobservationdenyreasons',
            self.closing_deny_reason
        )


    def _vocabulary_value(self, vocabulary, term):
        vocab_factory = getUtility(IVocabularyFactory, name=vocabulary)
        vocabulary = vocab_factory(self)
        try:
            value = vocabulary.getTerm(term)
            return value.title
        except LookupError:
            return u''

    def get_status(self):
        return api.content.get_state(self)

    def can_close(self):
        if self.get_status() == 'pending':
            questions = [v for v in self.values() if v.portal_type == 'Question']
            if len(questions) > 0:
                for q in questions:
                    if api.content.get_state(q) != 'closed':
                        return False
                return True

        return False

    def wf_location(self):
        if self.get_status() == 'closed':
            return 'Closed'
        elif self.get_status() != 'pending':
            return 'Review Expert'
        else:
            questions = self.values()
            if questions:
                question = questions[0]
                state = api.content.get_state(question)
                if state in ['draft', 'validate-answer', 'closed']:
                    return 'Review Expert'
                elif state in ['counterpart-comments']:
                    return 'CounterPart'
                elif state in ['drafted', 'recalled-lr', 'answered']:
                    return 'Lead Reviewer'
                elif state in ['pending',
                    'pending-answer-validation', 'recalled-msa']:
                    return 'MS Authority'
                elif state in ['pending-answer']:
                    return 'MS Expert'

            return 'Review Expert'

    def wf_status(self):
        if self.get_status() == 'draft':
            return 'Draft observation'
        elif self.get_status() == 'closed':
            return 'Closed observation'
        elif self.get_status() == 'close-requested':
            return 'Closure requested'
        elif self.get_status() in ['conclusions', 'conclusion-discussion']:
            return 'Conclusion drafting'
        else:
            questions = self.values()
            if questions:
                question = questions[0]
                state = api.content.get_state(question)
                if state in ['answered']:
                    return 'Pending question'
                elif state in ['pending', 'pending-answer', 'pending-answer-validation',
                    'validate-answer', 'recalled-msa']:
                    return 'Open question'
                elif state in ['draft', 'counterpart-comments',
                    'drafted', 'recalled-lr']:
                    return 'Draft question'
                elif state in ['closed']:
                    return 'Closed question'

    def observation_status(self):
        status = self.get_status()
        if status == 'draft':
            return 'draft'
        elif status == 'closed':
            return 'closed'
        elif status in ['close-requested', 'conclusions', 'conclusion-discussion']:
            return 'conclusions'
        else:
            return 'open'

    def is_secretariat(self):
        user = api.user.get_current()
        return 'Manager' in user.getRoles()

    def get_author_name(self, userid):
        if userid:
            user = api.user.get(username=userid)
            return user.getProperty('fullname', userid)
        return userid

    def myHistory(self):
        observation_history = self.workflow_history['esd-review-workflow']
        observation_wf = []
        question_wf = []
        for item in observation_history:
            item['role'] = item['actor']
            item['object'] = 'observation'
            item['author'] = self.get_author_name(item['actor'])
            if item['review_state'] == 'draft':
                item['state'] = 'Draft observation'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] == 'pending' and item['action'] == "approve":
                item['state'] = 'Pending'
                #Do not add
            elif item['review_state'] == 'pending' and item['action'] == "reopen":
                item['state'] = 'Observation reopened'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] == 'closed':
                item['state'] = 'Closed observation'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] == 'close-requested':
                item['state'] = 'Closure requested'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] == 'conclusions' and item['action'] == "deny-closure":
                item['state'] = 'Observation closure denied'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] in ['conclusion-discussion']:
                item['state'] = 'Conclusion comments requested'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] == 'conclusion' and item['action'] == "finish-comments":
                item['state'] = 'Conclusion comments closed'
                item['role'] = "Review expert"
                observation_wf.append(item)
            elif item['review_state'] == 'conclusion' and item['action'] == "draft-conclusions":
                item['state'] = 'Conclusion drafting'
                item['role'] = "Review expert"
                observation_wf.append(item)
            else:
                item['state'] = '*' + item['review_state'] + '*'
                observation_wf.append(item)

        history = list(observation_wf)
        questions = self.values()

        if questions:
            question = questions[0]

            question_history = question.workflow_history['esd-question-review-workflow']
            for item in question_history:
                item['role'] = item['actor']
                item['object'] = 'question'
                item['author'] = self.get_author_name(item['actor'])
                if item['review_state'] == 'draft' and item['action'] == None:
                    item['state'] = 'Draft question'
                    item['role'] = "Review expert"
                    question_wf.append(item)
                elif item['review_state'] == 'counterpart-comments':
                    item['state'] = 'Requested counterparts comments'
                    item['role'] = "Review expert"
                    question_wf.append(item)
                elif item['review_state'] == 'draft' and item['action'] =='send-comments':
                    item['state'] = 'Counterparts comments closed'
                    item['role'] = "Review expert"
                    question_wf.append(item)
                elif item['review_state'] == 'drafted':
                    item['state'] = 'Sent to LR'
                    item['role'] = "Review expert"
                    question_wf.append(item)
                elif item['review_state'] == 'draft' and item['action'] =='recall-sre':
                    item['state'] = 'Question recalled'
                    item['role'] = "Review expert"
                    question_wf.append(item)
                elif item['review_state'] == 'pending' and item['action'] == 'approve-question':
                    item['state'] = 'Question approved and sent to MSA'
                    item['role'] = "Lead reviewer"
                    question_wf.append(item)
                elif item['review_state'] == 'recalled-lr':
                    item['state'] = 'Question recalled'
                    item['role'] = "Lead reviewer"
                elif item['review_state'] == 'recalled-msa':
                    item['state'] = 'Question recalled'
                    item['role'] = "Question recalled"
                    question_wf.append(item)
                elif item['review_state'] == 'pending-answer':
                    item['state'] = 'Member state expert comments requested'
                    item['role'] = "Member state authority"
                    question_wf.append(item)
                elif item['review_state'] == 'pending-answer-validation':
                    item['state'] = 'Member state expert comments closed'
                    item['role'] = "Member state authority"
                    question_wf.append(item)
                elif item['review_state'] == 'answered':
                    item['state'] = 'Answer sent'
                    item['role'] = "Member state authority"
                    question_wf.append(item)
                elif item['action'] == 'validate-answer-msa':
                    item['state'] = 'Review expert'
                    item['role'] = "Answer acknowledged"
                    question_wf.append(item)
                elif item['review_state'] == 'draft' and item['action'] == "reopen":
                    item['state'] = 'Reopened'
                    #Do not add
                elif item['review_state'] == 'closed':
                    item['state'] = 'Closed'
                    #Do not add
                else:
                    item['state'] = '*' + item['review_state'] + '*'
                    item['role'] = item['actor']
                    question_wf.append(item)

            history = list(observation_wf) + list(question_wf)

        history.sort(key=lambda x: x["time"], reverse=False)
        return history

    def can_edit(self):
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', self)

    def get_question(self):
        questions = [q for q in self.values() if q.portal_type == 'Question']

        if questions:
            question = questions[0]
            return question
# View class
# The view will automatically use a similarly named template in
# templates called observationview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type

grok.templatedir('templates')


class AddForm(dexterity.AddForm):
    grok.name('esdrt.content.observation')
    grok.context(IObservation)
    grok.require('esdrt.content.AddObservation')

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        self.fields['IDublinCore.title'].field.required = False
        self.widgets['IDublinCore.title'].mode = interfaces.HIDDEN_MODE
        self.widgets['IDublinCore.description'].mode = interfaces.HIDDEN_MODE
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']

    def updateActions(self):
        super(AddForm, self).updateActions()
        self.actions['save'].title = u'Save Observation'
        self.actions['cancel'].title = u'Delete Observation'

        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


@grok.subscribe(IObservation, IObjectAddedEvent)
def add_question(context, event):
    """ When adding a question, go directly to
        'open' status on the observation
    """
    observation = context
    with api.env.adopt_roles(roles=['Manager']):
        if api.content.get_state(obj=observation) == 'draft':
            api.content.transition(obj=observation, transition='approve')


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
        tim = wf.getInfoFor(self.context,
            'time', wf_id='esd-review-workflow')
        return {'comments': comments, 'actor': actor, 'time': tim}

    def isManager(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)
        return sm.checkPermission('Manage portal', context)

    def get_user_name(self, userid):
        # Check users roles
        country = self.context.country_value()
        sector = self.context.ghg_source_sectors_value()
        return ' - '.join([country, sector])

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
        items = []
        mtool = api.portal.get_tool('portal_membership')
        for item in context.values():
            if item.portal_type == 'Question' and \
                mtool.checkPermission('View', item):
                items.append(item)

        return IContentListing(items)

    @property
    def repo_tool(self):
        return getToolByName(self.context, "portal_repository")

    def getVersion(self, version):
        question = self.question()
        context = question.getFirstComment()
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

    def can_delete_observation(self):
        is_draft = api.content.get_state(self.context) == 'pending'
        questions = len([q for q in self.context.values() if q.portal_type == 'Question'])

        return is_draft and not questions

    def can_add_question(self):
        sm = getSecurityManager()
        questions = len([q for q in self.context.values() if q.portal_type == 'Question'])
        return sm.checkPermission('esdrt.content: Add Question', self) and not questions

    def can_edit(self):
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', self.context)

    def get_conclusion(self):
        conclusions = [c for c in self.context.values() if c.portal_type == 'Conclusion']
        if conclusions:
            return conclusions[0]

        return None

    def can_add_conclusion(self):
        sm = getSecurityManager()
        conclusion = self.get_conclusion()
        return sm.checkPermission('esdrt.content: Add Conclusion', self.context) and not conclusion

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

    def show_description(self):
        questions = self.get_questions()
        sm = getSecurityManager()
        if questions:
            question = questions[-1]
            return sm.checkPermission('View', question.getObject())
        else:
            user = api.user.get_current()
            userroles = api.user.get_roles(username=user.getId(),
                obj=self.context)
            if 'MSAuthority' in userroles or 'MSExpert' in userroles:
                return False

            return True

    def add_question_form(self):
        from plone.z3cform.interfaces import IWrappedForm
        form_instance = AddQuestionForm(self.context, self.request)
        alsoProvides(form_instance, IWrappedForm)
        return form_instance()

    #Question view
    def question(self):
        questions = self.get_questions()
        if questions:
            return questions[0].getObject()

    def get_chat(self):
        sm = getSecurityManager()
        question = self.question()
        if question:
            values = [v for v in question.values() if sm.checkPermission('View', v)]
            #return question.values()
            return values

    def actions(self):
        context = aq_inner(self.context)
        question = self.question()
        observation_menu_items = getMenu(
            'plone_contentmenu_workflow',
            context,
            self.request
            )
        menu_items = observation_menu_items
        if question:
            question_menu_items = getMenu(
                'plone_contentmenu_workflow',
                question,
                self.request
                )

            menu_items = question_menu_items + observation_menu_items
        return [mitem for mitem in menu_items if not hidden(mitem)]

    def get_user_name(self, userid, question=None):
        # check users
        if question is not None:
            country = self.context.country_value()
            sector = self.context.ghg_source_sectors_value()
            if question.portal_type == 'Comment':
                return ' - '.join([country, sector])
            elif question.portal_type == 'CommentAnswer':
                return ' - '.join([country, 'Authority'])

        if userid:
            user = api.user.get(username=userid)
            return user.getProperty('fullname', userid)
        return ''

    def can_add_comment(self):
        sm = getSecurityManager()
        question = self.question()
        if question:
            permission = sm.checkPermission('esdrt.content: Add Comment', question)
            questions = [q for q in question.values() if q.portal_type == 'Comment']
            answers = [q for q in question.values() if q.portal_type == 'CommentAnswer']
            obs_state = self.context.get_status()
            return permission and len(questions) == len(answers) and obs_state != 'closed'
        else:
            return False

    def can_add_answer(self):
        sm = getSecurityManager()
        question = self.question()
        if question:
            permission = sm.checkPermission('esdrt.content: Add CommentAnswer', question)
            questions = [q for q in question.values() if q.portal_type == 'Comment']
            answers = [q for q in question.values() if q.portal_type == 'CommentAnswer']
            return permission and len(questions) > len(answers)
        else:
            return False

    def add_answer_form(self):
        form_instance = AddAnswerForm(self.context, self.request)
        alsoProvides(form_instance, IWrappedForm)
        return form_instance()

    def add_no_answer_form(self):
        form_instance = AddNoAnswerForm(self.context, self.request)
        alsoProvides(form_instance, IWrappedForm)
        return form_instance()

    def can_see_comments(self):
        state = api.content.get_state(self.question())
        #return state in ['draft', 'counterpart-comments', 'drafted']
        return state in ['counterpart-comments']

    def add_comment_form(self):
        form_instance = AddCommentForm(self.context, self.request)
        alsoProvides(form_instance, IWrappedForm)
        return form_instance()

    def add_conclusion_form(self):
        form_instance = AddConclusionForm(self.context, self.request)
        alsoProvides(form_instance, IWrappedForm)
        return form_instance()

    def update(self):
        question = self.question()
        if question:
            context = question.getFirstComment()
            if context.can_edit():
                try:
                    history_metadata = self.repo_tool.getHistoryMetadata(context)
                except:
                    history_metadata = None
                if history_metadata:
                    retrieve = history_metadata.retrieve
                    getId = history_metadata.getVersionId
                    history = self.history = []
                    # Count backwards from most recent to least recent
                    for i in xrange(history_metadata.getLength(countPurged=False)-1, -1, -1):
                        version = retrieve(i, countPurged=False)['metadata'].copy()
                        version['version_id'] = getId(i, countPurged=False)
                        history.append(version)
                    dt = getToolByName(self.context, "portal_diff")

                    version1 = self.request.get("one", None)
                    version2 = self.request.get("two", None)

                    if version1 is None and version2 is None:
                        self.history.sort(lambda x,y: cmp(x.get('version_id', ''), y.get('version_id')), reverse=True)
                        version1 = self.history[-1].get('version_id', 'current')
                        if len(self.history) > 1:
                            version2 = self.history[-2].get('version_id', 'current')
                        else:
                            version2 = 'current'
                    elif version1 is None:
                        version1 = 'current'
                    elif version2 is None:
                        version2 = 'current'

                    self.request.set('one', version1)
                    self.request.set('two', version2)

                    changeset = dt.createChangeSet(
                            self.getVersion(version2),
                            self.getVersion(version1),
                            id1=self.versionTitle(version2),
                            id2=self.versionTitle(version1))
                    self.changes = [change for change in changeset.getDiffs()
                                  if not change.same]
    #def get_chat(self):
    #    question = self.question()
    #    if question:
    #        return question.get_questions()




class AddQuestionForm(Form):

    ignoreContext = True
    fields = field.Fields(IComment).select('text')

    @button.buttonAndHandler(_('Save question'))
    def create_question(self, action):
        context = aq_inner(self.context)
        text = self.request.form.get('form.widgets.text', '')
        transforms = getToolByName(context, 'portal_transforms')
        stream = transforms.convertTo('text/plain', text, mimetype='text/html')
        text = stream.getData().strip()
        if not text:
            raise ActionExecutionError(Invalid(u"Question text is empty"))

        qs = [item for item in self.context.values() if item.portal_type == 'Question']
        if qs:
            question = qs[0]
        else:
            q_id = self.context.invokeFactory(type_name='Question',
                id='question-1',
                title='Question 1',
            )
            question = self.context.get(q_id)

        id = str(int(time()))
        item_id = question.invokeFactory(
                type_name='Comment',
                id=id,
        )
        comment = question.get(item_id)
        comment.text = RichTextValue(text, 'text/html', 'text/html')

        #return self.request.response.redirect(comment.absolute_url())
        return self.request.response.redirect(self.context.absolute_url())

    def updateActions(self):
        super(AddQuestionForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


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
        roles = api.user.get_roles(username=user.getId(), obj=self.context)
        fields = []
        # XXX Needed? Edit rights are controlled by the WF
        if 'SectorExpertReviewer' in roles:
            fields = [f for f in field.Fields(IObservation) if f not in [
                'country',
                'crf_code',
                'review_year',
                'technical_corrections',
                'closing_comments',
                'closing_reason',
                'closing_deny_comments',
                'closing_deny_reason',
                ]]
        elif 'LeadReviewer' in roles:
            fields = ['text']
        elif 'CounterPart' in roles:
            fields = ['text']

        self.fields = field.Fields(IObservation).select(*fields)
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']
        if 'status_flag' in fields:
            self.fields['status_flag'].widgetFactory = CheckBoxFieldWidget
        if 'ghg_estimations' in fields:
            self.fields['ghg_estimations'].widgetFactory = DataGridFieldFactory
        if 'parameter' in fields:
            self.fields['parameter'].widgetFactory = RadioFieldWidget
        if 'highlight' in fields:
            self.fields['highlight'].widgetFactory = CheckBoxFieldWidget


    def updateActions(self):
        super(ModificationForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class AddAnswerForm(Form):

    ignoreContext = True
    fields = field.Fields(IComment).select('text')

    @button.buttonAndHandler(_('Save answer'))
    def create_question(self, action):
        observation = aq_inner(self.context)
        questions = [q for q in observation.values() if q.portal_type == 'Question']
        if questions:
            context = questions[0]
        else:
            raise
        id = str(int(time()))
        item_id = context.invokeFactory(
                type_name='CommentAnswer',
                id=id,
        )
        text = self.request.form.get('form.widgets.text', '')
        comment = context.get(item_id)
        comment.text = RichTextValue(text, 'text/html', 'text/html')

        return self.request.response.redirect(context.absolute_url())

    def updateActions(self):
        super(AddAnswerForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')

class AddNoAnswerForm(Form):

    ignoreContext = True
    fields = field.Fields(IComment).select('text')

    @button.buttonAndHandler(_('Save no answer'))
    def create_question(self, action):
        observation = aq_inner(self.context)
        questions = [q for q in observation.values() if q.portal_type == 'Question']
        if questions:
            context = questions[0]
        else:
            raise
        id = str(int(time()))
        item_id = context.invokeFactory(
                type_name='CommentAnswer',
                id=id,
        )
        #text = self.request.form.get('form.widgets.text', '')
        text = 'No draft answer available so far'
        comment = context.get(item_id)
        comment.text = RichTextValue(text, 'text/html', 'text/html')

        return self.request.response.redirect(context.absolute_url() + "/assign_answerer_form?workflow_action=assign-answerer")

    def updateActions(self):
        super(AddNoAnswerForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class AddCommentForm(Form):

    ignoreContext = True
    fields = field.Fields(IComment).select('text')

    @button.buttonAndHandler(_('Add question'))
    def create_question(self, action):
        observation = aq_inner(self.context)
        questions = [q for q in observation.values() if q.portal_type == 'Question']
        if questions:
            context = questions[0]
        else:
            raise

        id = str(int(time()))
        item_id = context.invokeFactory(
                type_name='Comment',
                id=id,
        )
        text = self.request.form.get('form.widgets.text', '')
        comment = context.get(item_id)
        comment.text = RichTextValue(text, 'text/html', 'text/html')

        return self.request.response.redirect(context.absolute_url())

    def updateActions(self):
        super(AddCommentForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class AddConclusionForm(Form):
    ignoreContext = True
    fields = field.Fields(IConclusion).select('text', 'closing_reason')

    @button.buttonAndHandler(_('Add conclusion'))
    def create_conclusion(self, action):
        context = aq_inner(self.context)
        id = str(int(time()))
        item_id = context.invokeFactory(
                type_name='Conclusion',
                id=id,
        )
        text = self.request.form.get('form.widgets.text', '')
        comment = context.get(item_id)
        comment.text = RichTextValue(text, 'text/html', 'text/html')
        reason = self.request.form.get('form.widgets.closing_reason')
        comment.closing_reason = reason[0]

        return self.request.response.redirect(context.absolute_url())

    def updateActions(self):
        super(AddConclusionForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')