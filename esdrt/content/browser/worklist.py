from AccessControl import getSecurityManager
from five import grok
from plone import api
from plone.memoize.view import memoize
from zope.interface import Interface


grok.templatedir('templates')


class WorklistView(grok.View):
    grok.context(Interface)
    grok.name('worklistview')
    grok.require('zope2.View')

    @memoize
    def get_questions(self):
        catalog = api.portal.get_tool('portal_catalog')
        values = catalog.unrestrictedSearchResults(
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
