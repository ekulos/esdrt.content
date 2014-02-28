from zope.browsermenu.menu import getMenu
from plone.app.textfield.value import RichTextValue
from Acquisition import aq_parent
from plone.app.contentlisting.interfaces import IContentListing
from time import time
from Acquisition import aq_inner
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from Acquisition.interfaces import IAcquirer
from zope.component import createObject
from Acquisition import aq_base
from esdrt.content import MessageFactory as _
from esdrt.content.comment import IComment
from esdrt.content.observation import IObservation
from five import grok
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form import field
from plone import api

# Interface class; used to define content-type schema.
class IQuestion(form.Schema, IImageScaleTraversable):
    """
    New Question regarding an Observation
    """

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class Question(dexterity.Container):
    grok.implements(IQuestion)    # Add your class methods and properties here

    def get_questions(self):
        return IContentListing([v for v in self.values() if v.portal_type in ['Comment', 'CommentAnswer']])

    def getFirstComment(self):
        comments = [v for v in self.values() if v.portal_type == 'Comment']
        comments.sort(lambda x, y: cmp(x.created(), y.created()))
        if comments:
            return comments[-1]
        return None

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
        return getMenu(
            'plone_contentmenu_workflow',
            context,
            self.request
            )

    def get_user_name(self, userid):
        mtool = api.portal.get_tool('portal_membership')
        member = mtool.getMemberById(userid)
        if member is not None:
            return member.getProperty('fullname', userid)
        return ''


    def actions_for_comment(self, commentid):
        context = aq_inner(self.context)
        comment = context.get(commentid)
        return getMenu(
            'plone_contentmenu_workflow',
            comment,
            self.request
            )


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
