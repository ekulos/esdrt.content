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
        reviewYear = self.request.form.get('reviewYear', '')
        inventoryYear = self.request.form.get('inventoryYear', '')
        status = self.request.form.get('status', '')
        highlights = self.request.form.get('highlights', '')
        freeText = self.request.form.get('freeText', '')

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
                query['review_state'] = ['phase1-draft', 'phase2-draft'];
            elif status == "finished":
                query['review_state'] = ['phase1-closed', 'phase2-closed'];
            elif status == "conclusion":
                query['review_state'] = ['phase1-conclusions', 'phase2-conclusions', 'phase1-conclusion-discussion', 'phase2-conclusion-discussion'];
            else:
                query['review_state'] = ['phase1-pending', 'phase2-pending', 'phase1-close-requested', 'phase2-close-requested'];
        if (reviewYear != ""):
            query['review_year'] = reviewYear
        if (inventoryYear != ""):
            query['year'] = inventoryYear        
        if (highlights != ""):
            query['highlight'] = highlights.split(",")
        if (freeText != ""):
            query['SearchableText'] = freeText
   

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

    def get_review_years(self):
        catalog = api.portal.get_tool('portal_catalog')
        review_years = catalog.uniqueValuesFor('review_year')
        review_years = [c for c in  catalog.uniqueValuesFor('review_year') if isinstance(c, basestring)]
        return review_years

    def get_inventory_years(self):
        catalog = api.portal.get_tool('portal_catalog')
        inventory_years = catalog.uniqueValuesFor('year')
        return inventory_years

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
    @memoize
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
                                if (obj.observation_question_status() == 'observation-phase1-draft' or \
                                obj.observation_question_status() == 'observation-phase2-draft'):
                                    items.append(obj)
                    except:
                        pass
        return items          

    @memoize
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
                                obj.observation_question_status() == 'phase2-draft' or \
                                obj.observation_question_status() == 'phase1-counterpart-comments' or \
                                obj.observation_question_status() == 'phase2-counterpart-comments') and \
                                obj.last_question_reply_number() > 0:
                                    items.append(obj)
                    except:
                        pass
        return items 

    @memoize
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

    @memoize
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

    @memoize
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
                                if (obj.observation_question_status() == 'phase1-answered' or \
                                obj.observation_question_status() == 'phase2-answered'):
                                    items.append(obj)
                    except:
                        pass
        return items         

    @memoize
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
 
    @memoize
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

    @memoize
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

    @memoize    
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

    """
        Lead Reviewer / Quality expert
    """
    @memoize
    def get_questions_to_be_sent(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for me to send to the MS
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
                                if (obj.observation_question_status() == 'phase1-drafted' or \
                                obj.observation_question_status() == 'phase2-drafted' or \
                                obj.observation_question_status() == 'phase1-recalled-lr' or \
                                obj.observation_question_status() == 'phase2-recalled-lr'):
                                    items.append(obj)
                    except:
                        pass
        return items 

    @memoize
    def get_observations_to_finalise(self):
        """
         Role: Lead Reviewer / Quality expert
         Observations waiting for me to confirm finalisation
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

    @memoize
    def get_questions_to_comment(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for my comments
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

    @memoize
    def get_conclusions_to_comment(self):
        """
         Role: Lead Reviewer / Quality expert
         Conclusions waiting for my comments
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

    @memoize        
    def get_questions_with_comments_from_reviewers(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for comments by counterpart
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

    @memoize        
    def get_answers_from_ms(self):
        """
         Role: Lead Reviewer / Quality expert
         that need review by Sector Expert/Review expert
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
                                if (obj.observation_question_status() == 'phase1-answered' or \
                                obj.observation_question_status() == 'phase2-answered'):
                                    items.append(obj)
                    except:
                        pass
        return items    

    @memoize
    def get_unanswered_questions_lr_qe(self):
        """
         Role: Lead Reviewer / Quality expert
         questions waiting for comments from MS
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


    """
        MS Coordinator
    """
    @memoize    
    def get_questions_to_be_answered(self):
        """
         Role: MS Coordinator
         Questions from the SE/RE to be answered
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

    @memoize        
    def get_questions_with_comments_received_from_mse(self):
        """
         Role: MS Coordinator
         Comments received from MS Experts
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
                                if (obj.observation_question_status() == 'phase1-expert-comments' or \
                                obj.observation_question_status() == 'phase2-expert-comments') and \
                                obj.last_answer_reply_number() > 0:
                                    items.append(obj)
                    except:
                        pass
        return items  

    @memoize        
    def get_answers_requiring_comments_from_mse(self):
        """
         Role: MS Coordinator
         Answers requiring comments/discussion from MS experts
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
                                if (obj.observation_question_status() == 'phase1-expert-comments' or \
                                obj.observation_question_status() == 'phase2-expert-comments'):
                                    items.append(obj)
                    except:
                        pass
        return items   

    @memoize         
    def get_answers_sent_to_se_re(self):
        """
         Role: MS Coordinator
         Answers sent to SE/RE
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
                                if (obj.observation_question_status() == 'phase1-answered' or \
                                obj.observation_question_status() == 'phase2-answered'):
                                    items.append(obj)
                    except:
                        pass
        return items  
    """
        MS Expert
    """   
    @memoize        
    def get_questions_with_comments_for_answer_needed_by_msc(self):
        """
         Role: MS Expert
         Comments for answer needed by MS Coordinator
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
                                if (obj.observation_question_status() == 'phase1-expert-comments' or \
                                obj.observation_question_status() == 'phase2-expert-comments') and \
                                "CounterPart" in roles:
                                    items.append(obj)
                    except:
                        pass
        return items         
    @memoize        
    def get_observations_with_my_comments(self):
        """
         Role: MS Expert
         Observation I have commented on
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
                                if (obj.observation_question_status() == 'phase1-expert-comments' or \
                                obj.observation_question_status() == 'phase2-expert-comments' or \
                                obj.observation_question_status() == 'phase1-pending-answer-drafting' or \
                                obj.observation_question_status() == 'phase2-pending-answer-drafting') and \
                                "CounterPart" in roles and \
                                obj.reply_comments_by_mse():
                                    items.append(obj)
                    except:
                        pass
        return items        

    @memoize        
    def get_observations_with_my_comments_sent_to_se_re(self):
        """
         Role: MS Expert
         Answers that I commented on sent to Sector Expert/Review expert
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
                                if (obj.observation_question_status() == 'phase1-answered' or \
                                obj.observation_question_status() == 'phase2-answered' or \
                                obj.observation_question_status() == 'phase1-recalled-msa' or \
                                obj.observation_question_status() == 'phase2-recalled-msa') and \
                                "CounterPart" in roles and \
                                obj.reply_comments_by_mse():
                                    items.append(obj)
                    except:
                        pass
        return items  

    """
        Finalised observations
    """
    @memoize
    def get_no_response_needed_observations(self):
        """
         Finalised with 'no response needed'
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
                                if (obj.observation_question_status() == 'phase1-closed' or \
                                obj.observation_question_status() == 'phase2-closed') and \
                                obj.observation_finalisation_reason() == 'no-response-needed':
                                    items.append(obj)
                    except:
                        pass
        return items 
    @memoize
    def get_resolved_observations(self):
        """
         Finalised with 'resolved'
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
                                if (obj.observation_question_status() == 'phase1-closed' or \
                                obj.observation_question_status() == 'phase2-closed') and \
                                obj.observation_finalisation_reason() == 'resolved':
                                    items.append(obj)
                    except:
                        pass
        return items   
    @memoize
    def get_unresolved_observations(self):
        """
         Finalised with 'unresolved'
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
                                if (obj.observation_question_status() == 'phase1-closed' or \
                                obj.observation_question_status() == 'phase2-closed') and \
                                obj.observation_finalisation_reason() == 'unresolved':
                                    items.append(obj)
                    except:
                        pass
        return items   
    @memoize
    def get_partly_resolved_observations(self):
        """
         Finalised with 'partly resolved'
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
                                if (obj.observation_question_status() == 'phase1-closed' or \
                                obj.observation_question_status() == 'phase2-closed') and \
                                obj.observation_finalisation_reason() == 'partly-resolved':
                                    items.append(obj)
                    except:
                        pass
        return items 
    @memoize
    def get_technical_correction_observations(self):
        """
         Finalised with 'partly resolved'
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
                                if (obj.observation_question_status() == 'phase1-closed' or \
                                obj.observation_question_status() == 'phase2-closed') and \
                                obj.observation_finalisation_reason() == 'technical-correction':
                                    items.append(obj)
                    except:
                        pass
        return items    
    @memoize
    def get_revised_estimate_observations(self):
        """
         Finalised with 'partly resolved'
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
                                if (obj.observation_question_status() == 'phase1-closed' or \
                                obj.observation_question_status() == 'phase2-closed') and \
                                obj.observation_finalisation_reason() == 'revised-estimate':
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

    @memoize
    def is_lead_reviewer_or_quality_expert(self):
        user = api.user.get_current()
        return ("extranet-esd-ghginv-qualityexpert" in user.getGroups() or "extranet-esd-esdreview-leadreview" in user.getGroups())

    @memoize
    def is_member_state_coordinator(self):
        user = api.user.get_current()
        return "extranet-esd-countries-msa" in user.getGroups()

    @memoize
    def is_member_state_expert(self):
        user = api.user.get_current()
        return "extranet-esd-countries-msexpert" in user.getGroups()