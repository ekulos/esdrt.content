from AccessControl import getSecurityManager
from Acquisition import aq_inner
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from zope.interface import Interface

grok.templatedir('templates')


class WorklistView(grok.View):
    grok.context(Interface)
    grok.name('worklistview')
    grok.require('zope2.View')

    def get_observations(self):
        items = []
        sm = getSecurityManager()
        context = aq_inner(self.context)
        for item in context.values():
            if item.portal_type == 'Observation' and \
                sm.checkPermission('View', item):
                items.append(item)

        items.sort(lambda x, y: cmp(x.modified(), y.modified()))

        return IContentListing(items)
