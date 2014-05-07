from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition.interfaces import IAcquirer
from esdrt.content import MessageFactory as _
from five import grok
from plone import api
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from time import time
from z3c.form import field
from zope.component import createObject
from zope.component import getUtility


# Interface class; used to define content-type schema.
class ICommentAnswer(form.Schema, IImageScaleTraversable):
    """
    Answer for Questions
    """
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/comment.xml to define the content type
    # and add directives here as necessary.
    text = RichText(
        title=_(u'Text'),
        required=True,
        )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class CommentAnswer(dexterity.Container):
    grok.implements(ICommentAnswer)
    # Add your class methods and properties here

    def can_edit(self):
        sm = getSecurityManager()
        return sm.checkPermission('Modify portal content', self)

    def can_add_files(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add ESDRT File', self)

    def get_files(self):
        items = self.values()
        mtool = api.portal.get_tool('portal_membership')
        return [item for item in items if mtool.checkPermission('View', item)]


# View class
# The view will automatically use a similarly named template in
# templates called commentanswerview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class CommentAnswerView(grok.View):
    grok.context(ICommentAnswer)
    grok.require('zope2.View')
    grok.name('view')

    def render(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        url = '%s#%s' % (parent.absolute_url(), context.getId())

        return self.request.response.redirect(url)


class AddForm(dexterity.AddForm):
    grok.name('esdrt.content.commentanswer')
    grok.context(ICommentAnswer)
    grok.require('esdrt.content.AddCommentAnswer')

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = field.Fields(ICommentAnswer).select('text')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']

    def create(self, data={}):
        # import pdb; pdb.set_trace()
        # return super(AddForm, self).create(data)
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        container = aq_inner(self.context)
        content = createObject(fti.factory)
        if hasattr(content, '_setPortalTypeName'):
            content._setPortalTypeName(fti.getId())

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        if IAcquirer.providedBy(content):
            content = content.__of__(container)

        id = str(int(time()))
        content.title = id
        content.id = id
        text = self.request.form.get('form.widgets.text', '')
        content.text = RichTextValue(text, 'text/html', 'text/html')

        return aq_base(content)


class EditForm(dexterity.EditForm):
    grok.name('edit')
    grok.context(ICommentAnswer)
    grok.require('cmf.ModifyPortalContent')

    def updateFields(self):
        super(EditForm, self).updateFields()
        self.fields = field.Fields(ICommentAnswer).select('text')
        self.groups = [g for g in self.groups if g.label == 'label_schema_default']