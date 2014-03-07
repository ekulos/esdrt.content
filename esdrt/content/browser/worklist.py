from AccessControl import getSecurityManager
from five import grok
from plone import api
from zope.interface import Interface

grok.templatedir('templates')


class WorklistView(grok.View):
    grok.context(Interface)
    grok.name('worklistview')
    grok.require('zope2.View')

    def get_questions(self):
        items = []
        catalog = api.portal.get_tool('portal_catalog')
        sm = getSecurityManager()
        values = catalog.unrestrictedSearchResults(
            portal_type='Question',
            sort_on='modified',
            sort_order='reverse',
        )
        for brain in values:
            item = brain.getObject()
            if sm.checkPermission('View', item):
                items.append(item)

        return items

    def can_add_observation(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add Observation', self)
