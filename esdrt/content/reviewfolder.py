from plone.memoize.view import memoize
from plone import api
from AccessControl import getSecurityManager
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

    @memoize
    def get_questions(self):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        values = catalog.unrestrictedSearchResults(
            path=path,
            portal_type=['Observation', 'Question'],
            sort_on='modified',
            sort_order='reverse',
        )
        items = []
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        for item in values:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                items.append(obj)
                    except:
                        pass

        return items

    def can_add_observation(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add Observation', self)

    def is_secretariat(self):
        user = api.user.get_current()
        return 'Manager' in user.getRoles()

    def get_author_name(self, userid):
        user = api.user.get(userid)
        return user.getProperty('fullname', userid)