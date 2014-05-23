from five import grok
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable


# Interface class; used to define content-type schema.
class IReviewFolder(form.Schema, IImageScaleTraversable):
    """
    Folder to have all observations together
    """


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class ReviewFolder(dexterity.Container):
    grok.implements(IReviewFolder)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called reviewfolderview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class ReviewFolderView(grok.View):
    grok.context(IReviewFolder)
    grok.require('zope2.View')
    grok.name('view')
