from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from plone.app.textfield import RichText
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from esdrt.content import MessageFactory as _


# Interface class; used to define content-type schema.
class IComment(form.Schema, IImageScaleTraversable):
    """
    Q&A item
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
class Comment(dexterity.Container):
    grok.implements(IComment)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called commentview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class CommentView(grok.View):
    grok.context(IComment)
    grok.require('zope2.View')
    grok.name('view')

    def render(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        url = '%s#%s' % (parent.absolute_url(), context.getId())

        return self.request.response.redirect(url)
