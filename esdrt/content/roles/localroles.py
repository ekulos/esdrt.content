from Acquisition import aq_inner
from Acquisition import aq_parent
from borg.localrole.interfaces import ILocalRoleProvider
from esdrt.content.comment import IComment
from esdrt.content.commentanswer import ICommentAnswer
from esdrt.content.observation import IObservation
from esdrt.content.question import IQuestion
from esdrt.content.conclusion import IConclusion
from esdrt.content.conclusionsphase2 import IConclusionsPhase2
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
        sector = context.ghg_source_category_value()
        mtool = getToolByName(context, 'portal_membership')
        roles = []
        member = mtool.getMemberById(principal_id)
        if member is not None:
            groups = member.getGroups()
            for group in groups:
                if 'extranet-esd-ghginv-sr-%s-%s' % (sector, country) in group:
                    roles.append('ReviewerPhase1')
                if 'extranet-esd-ghginv-qualityexpert-%s' % sector in group:
                    roles.append('QualityExpert')
                if 'extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country) in group:
                    roles.append('ReviewerPhase2')
                if 'extranet-esd-esdreview-leadreview-%s' % country in group:
                    roles.append('LeadReviewer')
                if 'extranet-esd-countries-msa-%s' % country in group:
                    roles.append('MSAuthority')
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
            sector = observation.ghg_source_category_value()
            mtool = getToolByName(observation, 'portal_membership')
            member = mtool.getMemberById(principal_id)
            if member is not None:
                groups = member.getGroups()
                for group in groups:
                    if 'extranet-esd-ghginv-sr-%s-%s' % (sector, country) in group:
                        roles.append('ReviewerPhase1')
                    if 'extranet-esd-ghginv-qualityexpert-%s' % sector in group:
                        roles.append('QualityExpert')
                    if 'extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country) in group:
                        roles.append('ReviewerPhase2')
                    if 'extranet-esd-esdreview-leadreview-%s' % country in group:
                        roles.append('LeadReviewer')
                    if 'extranet-esd-countries-msa-%s' % country in group:
                        roles.append('MSAuthority')
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
                sector = observation.ghg_source_category_value()
                mtool = getToolByName(comment, 'portal_membership')
                member = mtool.getMemberById(principal_id)
                if member is not None:
                    groups = member.getGroups()
                    for group in groups:
                        if 'extranet-esd-ghginv-sr-%s-%s' % (sector, country) in group:
                            roles.append('ReviewerPhase1')
                        if 'extranet-esd-ghginv-qualityexpert-%s' % sector in group:
                            roles.append('QualityExpert')
                        if 'extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country) in group:
                            roles.append('ReviewerPhase2')
                        if 'extranet-esd-esdreview-leadreview-%s' % country in group:
                            roles.append('LeadReviewer')
                        if 'extranet-esd-countries-msa-%s' % country in group:
                            roles.append('MSAuthority')

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
                sector = observation.ghg_source_category_value()
                mtool = getToolByName(commentanswer, 'portal_membership')
                member = mtool.getMemberById(principal_id)
                if member is not None:
                    groups = member.getGroups()
                    for group in groups:
                        if 'extranet-esd-ghginv-sr-%s-%s' % (sector, country) in group:
                            roles.append('ReviewerPhase1')
                        if 'extranet-esd-ghginv-qualityexpert-%s' % sector in group:
                            roles.append('QualityExpert')
                        if 'extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country) in group:
                            roles.append('ReviewerPhase2')
                        if 'extranet-esd-esdreview-leadreview-%s' % country in group:
                            roles.append('LeadReviewer')
                        if 'extranet-esd-countries-msa-%s' % country in group:
                            roles.append('MSAuthority')

        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []


class ConclusionRoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(IConclusion)

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
            sector = observation.ghg_source_category_value()
            mtool = getToolByName(observation, 'portal_membership')
            member = mtool.getMemberById(principal_id)
            if member is not None:
                groups = member.getGroups()
                for group in groups:
                    if 'extranet-esd-ghginv-sr-%s-%s' % (sector, country) in group:
                        roles.append('ReviewerPhase1')
                    if 'extranet-esd-ghginv-qualityexpert-%s' % sector in group:
                        roles.append('QualityExpert')
                    if 'extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country) in group:
                        roles.append('ReviewerPhase2')
                    if 'extranet-esd-esdreview-leadreview-%s' % country in group:
                        roles.append('LeadReviewer')
                    if 'extranet-esd-countries-msa-%s' % country in group:
                        roles.append('MSAuthority')
        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []


class ConclusionPhase2RoleAdapter(object):
    implements(ILocalRoleProvider)
    adapts(IConclusionsPhase2)

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
            sector = observation.ghg_source_category_value()
            mtool = getToolByName(observation, 'portal_membership')
            member = mtool.getMemberById(principal_id)
            if member is not None:
                groups = member.getGroups()
                for group in groups:
                    if 'extranet-esd-ghginv-sr-%s-%s' % (sector, country) in group:
                        roles.append('ReviewerPhase1')
                    if 'extranet-esd-ghginv-qualityexpert-%s' % sector in group:
                        roles.append('QualityExpert')
                    if 'extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country) in group:
                        roles.append('ReviewerPhase2')
                    if 'extranet-esd-esdreview-leadreview-%s' % country in group:
                        roles.append('LeadReviewer')
                    if 'extranet-esd-countries-msa-%s' % country in group:
                        roles.append('MSAuthority')
        return roles

    def getAllRoles(self):
        """Returns all the local roles assigned in this context:
        (principal_id, [role1, role2])"""
        return []