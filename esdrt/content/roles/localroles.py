from Acquisition import aq_inner
from borg.localrole.interfaces import ILocalRoleProvider
from esdrt.content.observation import IObservation
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements


class ObservationRoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(IObservation)

    def __init__(self, context):
        self.context = context

    # def getDummyRolesOnContext(self, context, principal_id):
    #     """ Calculate magical Dummy roles based on the user object.

    #     Note: This function is *heavy* since it wakes lots of objects
    #      along the acquisition chain.
    #     """

    #     # Filter out bogus look-ups - Plone calls this function
    #     # for every possible role look up out there, but
    #     # we are interested only these two cases
    #     if IObservation.providedBy(context):
    #             return ["Dummy Member"]

    #     # No match
    #     return []

    def getRoles(self, principal_id):
        """Returns the roles for the given principal in context.

        This function is additional besides other ILocalRoleProvider plug-ins.

        @param context: Any Plone object
        @param principal_id: User login id
        """
        context = aq_inner(self.context)
        country = context.country.lower()
        sector = context.ghg_source_sectors
        mtool = getToolByName(context, 'portal_membership')
        roles = []
        member = mtool.getMemberById(principal_id)
        if member is not None:
            groups = member.getGroups()
            for group in groups:
                if 'leadreviewers-%s' % country in group:
                    roles.append('LeadReviewer')
                if 'ms-authorities-%s' % country in group:
                    roles.append('MSAuthority')
                if 'ms-authorities-%s' % country in group:
                    roles.append('MSAuthority')
                if 'ms-experts-%s' % country in group:
                    roles.append('MSExpert')
                if 'ms-reviewexperts-%s' % sector in group:
                    roles.append('ExpertReviewer')
        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []
