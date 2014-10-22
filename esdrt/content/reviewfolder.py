from plone.memoize.view import memoize
from plone import api
from AccessControl import getSecurityManager
from five import grok
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName
from zope import schema
from esdrt.content import MessageFactory as _


# Interface class; used to define content-type schema.
class IReviewFolder(form.Schema, IImageScaleTraversable):
    """
    Folder to have all observations together
    """
    year = schema.Int(
        title=_(u'Year'),
        required=True,
        )

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
        country = self.request.form.get('country', '')
        reviewYearFilter = self.request.form.get('reviewYearFilter', '')
        inventoryYearFilter = self.request.form.get('inventoryYearFilter', '')
        status = self.request.form.get('status', '')

        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path':path,
            'portal_type':['Observation', 'Question'],
            'sort_on':'modified',
            'sort_order':'reverse',
        }
        if (country != ""):
            query['Country'] = country;
        if (status != ""):
            if status == "draft":
                query['review_state'] = "draft";
            elif status == "finished":
                query['review_state'] = "closed";
            elif status == "conclusion":
                query['review_state'] = ['conclusions', 'conclusion-discussion'];
            else:
                query['review_state'] = ['pending', 'close-requested'];
        if (reviewYearFilter != ""):
            query['reviewYear'] = reviewYearFilter
        if (inventoryYearFilter != ""):
            query['inventoryYear'] = inventoryYearFilter        
            

            

        values = catalog.unrestrictedSearchResults(query)
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

    def get_countries(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('eea_member_states')
        countries = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            countries.append((term[0], term[1]))

        return countries        

    def get_highlights(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('highlight')
        highlights = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            highlights.append((term[0], term[1]))

        return highlights          


class InboxReviewFolderView(grok.View):
    grok.context(IReviewFolder)
    grok.require('zope2.View')
    grok.name('inboxview')

    def update(self):
        self.observations = self.get_all_observations()

    def get_all_observations(self):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path':path,
            'portal_type':'Observation',
            'sort_on':'modified',
            'sort_order':'reverse',
        }
            
        values = catalog.unrestrictedSearchResults(query)
        return values

    """
        Sector expert / Review expert
    """
    def get_draft_observations(self):
        """
         Role: Sector expert / Review expert
         without actions for LR, counterpart or MS
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-draft' or \
                                obj.observation_question_status() == 'phase2-draft'):
                                    items.append(obj)
                    except:
                        pass
        return items          

    def get_draft_questions(self):
        """
         Role: Sector expert / Review expert
         with comments from counterpart of LR
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-draft' or \
                                obj.observation_question_status() == 'phase2-draft'):
                                    items.append(obj)
                    except:
                        pass
        return items 

    def get_counterpart_questions_to_comment(self):
        """
         Role: Sector expert / Review expert
         needing comment from me
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        roles = api.user.get_roles(username=user.id, obj=obj)
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-counterpart-comments' or \
                                obj.observation_question_status() == 'phase2-counterpart-comments') and \
                                "CounterPart" in roles:
                                    items.append(obj)
                    except:
                        pass
        return items 

    def get_counterpart_conclusion_to_comment(self):
        """
         Role: Sector expert / Review expert
         needing comment from me
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        roles = api.user.get_roles(username=user.id, obj=obj)
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-conclusion-discussion' or \
                                obj.observation_question_status() == 'phase2-conclusion-discussion') and \
                                "CounterPart" in roles:
                                    items.append(obj)
                    except:
                        pass
        return items 

    def get_ms_answers_to_review(self):
        """
         Role: Sector expert / Review expert
         that need review
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                import pdb; pdb.set_trace()
                                if (obj.observation_question_status() == 'phase1-answered' or \
                                obj.observation_question_status() == 'phase2-answered'):
                                    items.append(obj)
                    except:
                        pass
        return items         


    def get_unanswered_questions(self):
        """
         Role: Sector expert / Review expert
         my questions sent to LR and MS and waiting for reply
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-pending' or \
                                obj.observation_question_status() == 'phase2-pending' or \
                                obj.observation_question_status() == 'phase1-recalled-msa' or \
                                obj.observation_question_status() == 'phase2-recalled-msa'):
                                    items.append(obj)
                    except:
                        pass
        return items 
 
    def get_waiting_for_comment_from_counterparts_for_question(self):
        """
         Role: Sector expert / Review expert
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        roles = api.user.get_roles(username=user.id, obj=obj)
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-counterpart-comments' or \
                                obj.observation_question_status() == 'phase2-counterpart-comments') and \
                                "CounterPart" not in roles:
                                    items.append(obj)
                    except:
                        pass
        return items 

    def get_waiting_for_comment_from_counterparts_for_conclusion(self):
        """
         Role: Sector expert / Review expert
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        roles = api.user.get_roles(username=user.id, obj=obj)
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-conclusion-discussion' or \
                                obj.observation_question_status() == 'phase2-conclusion-discussion') and \
                                "CounterPart" not in roles:
                                    items.append(obj)
                    except:
                        pass
        return items 

    def get_observation_for_finalisation(self):
        """
         Role: Sector expert / Review expert
         waiting approval from LR
        """
        user = api.user.get_current()
        mtool = api.portal.get_tool('portal_membership')
        items = []
        for item in self.observations:
            if 'Manager' in user.getRoles():
                items.append(item.getObject())
            else:
                with api.env.adopt_roles(['Manager']):
                    try:
                        obj = item.getObject()
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-close-requested' or \
                                obj.observation_question_status() == 'phase2-close-requested'):
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

    def get_countries(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('eea_member_states')
        countries = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            countries.append((term[0], term[1]))

        return countries        

    def get_sectors(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('ghg_source_sectors')
        sectors = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            sectors.append((term[0], term[1]))

        return sectors      

    @memoize
    def is_sector_expert_or_review_expert(self):
        user = api.user.get_current()
        return ("extranet-esd-ghginv-sr" in user.getGroups() or "extranet-esd-esdreview-reviewexp" in user.getGroups())

    def is_review_expert(self):
        user = api.user.get_current()
        return "ExpertReviewer" in user.getRoles()

    @memoize
    def is_lead_reviewer(self):
        user = api.user.get_current()
        return "LeadReviewer" in user.getRoles()

    @memoize
    def is_quality_expert(self):
        user = api.user.get_current()
        return "QualityExpert" in user.getRoles()

    @memoize
    def is_member_state_authority(self):
        user = api.user.get_current()
        return "MSAuthority" in user.getRoles()

