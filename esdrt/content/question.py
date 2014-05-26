from zope.app.container.interfaces import IObjectAddedEvent
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition.interfaces import IAcquirer
from esdrt.content import MessageFactory as _
from esdrt.content.comment import IComment
from esdrt.content.observation import hidden
from five import grok
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName
from time import time
from z3c.form import field
from zope.browsermenu.menu import getMenu
from zope.component import createObject
from zope.component import getUtility


class IQuestion(form.Schema, IImageScaleTraversable):
    """
    New Question regarding an Observation
    """

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

PENDING_STATUS_NAMES = ['answered']
OPEN_STATUS_NAMES = ['pending', 'pending-answer', 'pending-answer-validation',
     'validate-answer', 'recalled-msa']
DRAFT_STATUS_NAMES = ['draft', 'counterpart-comments',
    'drafted', 'recalled-lr']
CLOSED_STATUS_NAMES = ['closed']

PENDING_STATUS_NAME = 'pending'
DRAFT_STATUS_NAME = 'draft'
OPEN_STATUS_NAME = 'open'
CLOSED_STATUS_NAME = 'closed'


class Question(dexterity.Container):
    grok.implements(IQuestion)    # Add your class methods and properties here

    def get_questions(self):
        sm = getSecurityManager()
        values = [v for v in self.values() if sm.checkPermission('View', v)]
        return IContentListing(values)

    def getFirstComment(self):
        comments = [v for v in self.values() if v.portal_type == 'Comment']
        comments.sort(lambda x, y: cmp(x.created(), y.created()))
        if comments:
            return comments[-1]
        return None

    def get_state(self):
        state = api.content.get_state(self)
        workflows = api.portal.get_tool('portal_workflow').getWorkflowsFor(self)
        if workflows:
            for w in workflows:
                if state in w.states:
                    return w.states[state].title or state

    def get_status(self):
        state = api.content.get_state(self)
        if state in PENDING_STATUS_NAMES:
            return PENDING_STATUS_NAME
        elif state in OPEN_STATUS_NAMES:
            return OPEN_STATUS_NAME
        elif state in CLOSED_STATUS_NAMES:
            return CLOSED_STATUS_NAME
        elif state in DRAFT_STATUS_NAMES:
            return DRAFT_STATUS_NAME

        return 'unknown'

    def get_observation(self):
        return aq_parent(aq_inner(self))

    def has_answers(self):
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        return len(questions) == len(answers)

    def unanswered_questions(self):
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        return len(questions) > len(answers)

    def can_close(self):
        """
        Check if this question can be closed:
            - There has been at least, one question-answer.
        """
        items = self.values()
        questions = [q for q in items if q.portal_type == 'Comment']
        answers = [q for q in items if q.portal_type == 'CommentAnswer']

        return len(questions) > 0 and len(questions) == len(answers)

    def observation_not_closed(self):
        observation = self.get_observation()
        return api.content.get_state(observation) == 'pending'

    def already_commented_by_counterpart(self):
        wtool = getToolByName(self, 'portal_workflow')
        wfinfo = wtool.getInfoFor(self,
            'review_history', 'esd-question-review-workflow')
        passed_states = [s['review_state'] for s in wfinfo]
        return 'counterpart-comments' in passed_states

    def one_pending_answer(self):
        if self.has_answers():
            answers = [q for q in self.values() if q.portal_type == 'CommentAnswer']
            answer = answers[-1]
            user = api.user.get_current()
            return answer.Creator() == user.getId()
        else:
            return False

# View class
# The view will automatically use a similarly named template in
# templates called questionview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type

grok.templatedir('templates')


class QuestionView(grok.View):
    grok.context(IQuestion)
    grok.require('zope2.View')
    grok.name('view')

    def observation(self):
        return aq_parent(aq_inner(self.context))

    def actions(self):
        context = aq_inner(self.context)
        menu_items = getMenu(
            'plone_contentmenu_workflow',
            context,
            self.request
            )
        return [mitem for mitem in menu_items if not hidden(mitem)]

    def get_user_name(self, userid, question=None):
        # check users
        if question is not None:
            obs = aq_parent(self.context)
            country = obs.country_value()
            sector = obs.ghg_source_sectors_value()
            if question.portal_type == 'Comment':
                return ' - '.join([country, sector])
            elif question.portal_type == 'CommentAnswer':
                return ' - '.join([country, 'Authority'])

        if userid:
            user = api.user.get(username=userid)
            return user.getProperty('fullname', userid)
        return ''

    def actions_for_comment(self, commentid):
        context = aq_inner(self.context)
        comment = context.get(commentid)
        return getMenu(
            'plone_contentmenu_workflow',
            comment,
            self.request
            )

    def can_add_comment(self):
        sm = getSecurityManager()
        permission = sm.checkPermission('esdrt.content: Add Comment', self)
        context = aq_inner(self.context)
        questions = [q for q in context.values() if q.portal_type == 'Comment']
        answers = [q for q in context.values() if q.portal_type == 'CommentAnswer']
        obs_state = api.content.get_state(obj=self.observation())
        return permission and len(questions) == len(answers) and obs_state != 'closed'

    def can_add_answer(self):
        sm = getSecurityManager()
        permission = sm.checkPermission('esdrt.content: Add CommentAnswer', self)
        context = aq_inner(self.context)
        questions = [q for q in context.values() if q.portal_type == 'Comment']
        answers = [q for q in context.values() if q.portal_type == 'CommentAnswer']
        return permission and len(questions) > len(answers)

    def wf_info(self):
        context = aq_inner(self.context)
        wf = getToolByName(context, 'portal_workflow')
        comments = wf.getInfoFor(self.context,
            'comments', wf_id='esd-question-review-workflow')
        actor = wf.getInfoFor(self.context,
            'actor', wf_id='esd-question-review-workflow')
        time = wf.getInfoFor(self.context,
            'time', wf_id='esd-question-review-workflow')
        return {'comments': comments, 'actor': actor, 'time': time}


class AddForm(dexterity.AddForm):
    grok.name('esdrt.content.question')
    grok.context(IQuestion)
    grok.require('esdrt.content.AddQuestion')

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = field.Fields(IComment).select('text')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']

    def create(self, data={}):
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        container = aq_inner(self.context)
        content = createObject(fti.factory)
        if hasattr(content, '_setPortalTypeName'):
            content._setPortalTypeName(fti.getId())

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        if IAcquirer.providedBy(content):
            content = content.__of__(container)
        context = self.context
        ids = [id for id in context.keys() if id.startswith('question-')]
        id = len(ids) + 1
        content.title = 'Question %d' % id

        return aq_base(content)

    def add(self, object):
        super(AddForm, self).add(object)
        item = self.context.get(object.getId())
        text = self.request.form.get('form.widgets.text', '')
        id = str(int(time()))
        item_id = item.invokeFactory(
            type_name='Comment',
            id=id,
        )
        comment = item.get(item_id)
        comment.text = RichTextValue(text, 'text/html', 'text/html')


@grok.subscribe(IQuestion, IObjectAddedEvent)
def add_question(context, event):
    """ When adding a question, go directly to
        'open' status on the observation
    """
    observation = aq_parent(context)
    with api.env.adopt_roles(roles=['Manager']):
        if api.content.get_state(obj=observation) == 'draft':
            api.content.transition(obj=observation, transition='approve')
