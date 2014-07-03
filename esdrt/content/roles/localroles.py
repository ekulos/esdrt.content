from Acquisition import aq_inner
from Acquisition import aq_parent
from borg.localrole.interfaces import ILocalRoleProvider
from esdrt.content.comment import IComment
from esdrt.content.commentanswer import ICommentAnswer
from esdrt.content.observation import IObservation
from esdrt.content.question import IQuestion
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements


class ObservationRoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(IObservation)

    def __init__(self, context):
        self.context = context

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
                if 'reviewexperts-%s-%s' % (sector, country) in group:
                    roles.append('SectorExpertReviewer')
                if 'leadreviewers-%s' % country in group:
                    roles.append('LeadReviewer')
                if 'ms-authorities-%s' % country in group:
                    roles.append('MSAuthority')
                # if 'ms-experts-%s' % country in group:
                #     roles.append('MSExpert')
        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []


class QuestionRoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(IQuestion)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        """Returns the roles for the given principal in context.

        This function is additional besides other ILocalRoleProvider plug-ins.

        @param context: Any Plone object
        @param principal_id: User login id
        """
        observation = aq_parent(aq_inner(self.context))
        roles = []
        if IObservation.providedBy(observation):
            country = observation.country.lower()
            sector = observation.ghg_source_sectors
            mtool = getToolByName(observation, 'portal_membership')
            member = mtool.getMemberById(principal_id)
            if member is not None:
                groups = member.getGroups()
                for group in groups:
                    if 'reviewexperts-%s-%s' % (sector, country) in group:
                        roles.append('SectorExpertReviewer')
                    if 'leadreviewers-%s' % country in group:
                        roles.append('LeadReviewer')
                    if 'ms-authorities-%s' % country in group:
                        roles.append('MSAuthority')
                    # if 'ms-experts-%s' % country in group:
                    #     roles.append('MSExpert')
        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []


class CommentRoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(IComment)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        """Returns the roles for the given principal in context.

        This function is additional besides other ILocalRoleProvider plug-ins.

        @param context: Any Plone object
        @param principal_id: User login id
        """
        comment = aq_inner(self.context)
        question = aq_parent(aq_inner(self.context))
        roles = []
        if IQuestion.providedBy(question):
            observation = aq_parent(question)
            if IObservation.providedBy(observation):
                country = observation.country.lower()
                sector = observation.ghg_source_sectors
                mtool = getToolByName(comment, 'portal_membership')
                member = mtool.getMemberById(principal_id)
                if member is not None:
                    groups = member.getGroups()
                    for group in groups:
                        if 'reviewexperts-%s-%s' % (sector, country) in group:
                            roles.append('SectorExpertReviewer')
                        if 'leadreviewers-%s' % country in group:
                            roles.append('LeadReviewer')
                        if 'ms-authorities-%s' % country in group:
                            roles.append('MSAuthority')
                        # if 'ms-experts-%s' % country in group:
                        #     roles.append('MSExpert')

        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []


class CommentAnswerRoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(ICommentAnswer)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        """Returns the roles for the given principal in context.

        This function is additional besides other ILocalRoleProvider plug-ins.

        @param context: Any Plone object
        @param principal_id: User login id
        """
        commentanswer = aq_inner(self.context)
        question = aq_parent(aq_inner(self.context))
        roles = []
        if IQuestion.providedBy(question):
            observation = aq_parent(question)
            if IObservation.providedBy(observation):
                country = observation.country.lower()
                sector = observation.ghg_source_sectors
                mtool = getToolByName(commentanswer, 'portal_membership')
                member = mtool.getMemberById(principal_id)
                if member is not None:
                    groups = member.getGroups()
                    for group in groups:
                        if 'reviewexperts-%s-%s' % (sector, country) in group:
                            roles.append('SectorExpertReviewer')
                        if 'leadreviewers-%s' % country in group:
                            roles.append('LeadReviewer')
                        if 'ms-authorities-%s' % country in group:
                            roles.append('MSAuthority')
                        # if 'ms-experts-%s' % country in group:
                        #     roles.append('MSExpert')

        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []
