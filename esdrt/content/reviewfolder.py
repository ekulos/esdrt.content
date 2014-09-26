from plone.memoize.view import memoize
from plone import api
from AccessControl import getSecurityManager
from five import grok
from plone.directives import dexterity
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName


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
        country = self.request.form.get('country', '')
        sector = self.request.form.get('sector', '')
        status = self.request.form.get('status', '')
        year = self.request.form.get('year', '')

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
        if (sector != ""):
            query['GHG_Source_Sectors'] = sector;
        if (status != ""):
            if status == "draft":
                query['review_state'] = "draft";
            elif status == "finished":
                query['review_state'] = "closed";
            elif status == "conclusion":
                query['review_state'] = ['conclusions', 'conclusion-discussion'];
            else:
                query['review_state'] = ['pending', 'close-requested'];
            

            

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

    def get_sectors(self):
        vtool = getToolByName(self, 'portal_vocabularies')
        voc = vtool.getVocabularyByName('ghg_source_sectors')
        sectors = []
        voc_terms = voc.getDisplayList(self).items()
        for term in voc_terms:
            sectors.append((term[0], term[1]))

        return sectors          


class InboxReviewFolderView(grok.View):
    grok.context(IReviewFolder)
    grok.require('zope2.View')
    grok.name('inboxview')

    @memoize
    def get_questions(self):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path':path,
            'portal_type':['Observation', 'Question'],
            'sort_on':'modified',
            'sort_order':'reverse',
        }
            
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

    @memoize
    def get_questions_reported_by_me(self):
        if self.is_review_expert():
            catalog = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            query = {
                'path':path,
                'portal_type':['Observation', 'Question'],
                'sort_on':'modified',
                'sort_order':'reverse',
            }
                
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
                            owner = obj.getOwner()
                            with api.env.adopt_user(user=user):
                                if mtool.checkPermission('View', obj):
                                    if user.id == owner._id:
                                        items.append(obj)
                        except:
                            pass

            return items

    def get_questions_as_counterpart(self):
        if self.is_review_expert() or self.is_lead_reviewer() or self.is_quality_expert():
            catalog = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            query = {
                'path':path,
                'portal_type':['Observation', 'Question'],
                'sort_on':'modified',
                'sort_order':'reverse',
            }
                
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
                            owner = obj.getOwner()
                            roles = api.user.get_roles(username=user.id, obj=obj)
                            with api.env.adopt_user(user=user):
                                if mtool.checkPermission('View', obj):
                                    if (obj.observation_question_status() == "phase1-counterpart-comments" or obj.observation_question_status() == "phase2-counterpart-comments") \
                                    and (user.id == owner._id or "CounterPart" in roles):
                                        items.append(obj)
                        except:
                            pass

            return items    

    def get_questions_replied_by_msa(self):
        if self.is_review_expert():
            catalog = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            query = {
                'path':path,
                'portal_type':['Observation', 'Question'],
                'sort_on':'modified',
                'sort_order':'reverse',
            }
                
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
                            owner = obj.getOwner()
                            with api.env.adopt_user(user=user):
                                if mtool.checkPermission('View', obj):
                                    if (obj.observation_question_status() == 'phase1-answered' or \
                                        obj.observation_question_status() == 'phase2-answered') \
                                     and user.id == owner._id:
                                        items.append(obj)
                        except:
                            pass

            return items            

    def get_questions_for_approval(self):
        if self.is_lead_reviewer() or self.is_quality_expert():
            catalog = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            query = {
                'path':path,
                'portal_type':['Observation', 'Question'],
                'sort_on':'modified',
                'sort_order':'reverse',
            }
                
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
                                    if (obj.observation_question_status() == 'phase1-drafted' or obj.observation_question_status() == 'phase2-drafted'):
                                        items.append(obj)
                        except:
                            pass

            return items 

    def get_questions_finalisation_requested(self):
        if self.is_lead_reviewer() or self.is_quality_expert():
            catalog = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            query = {
                'path':path,
                'portal_type':['Observation', 'Question'],
                'sort_on':'modified',
                'sort_order':'reverse',
            }
                
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
                                    if (obj.observation_question_status() == 'phase1-close-requested' or obj.observation_question_status() == 'phase2-close-requested'):
                                        items.append(obj)
                        except:
                            pass

            return items 

    def get_questions_answer_pending(self):
        if self.is_member_state_authority():
            catalog = api.portal.get_tool('portal_catalog')
            path = '/'.join(self.context.getPhysicalPath())
            query = {
                'path':path,
                'portal_type':['Observation', 'Question'],
                'sort_on':'modified',
                'sort_order':'reverse',
            }
                
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
                                    if (obj.observation_question_status() == 'phase1-pending' or obj.observation_question_status() == 'phase2-pending'):
                                        items.append(obj)
                        except:
                            pass

            return items 

    def get_questions_mse_comments_requested(self):
        country = self.request.form.get('country', '')
        sector = self.request.form.get('sector', '')
        status = self.request.form.get('status', '')
        year = self.request.form.get('year', '')

        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path':path,
            'portal_type':['Observation', 'Question'],
            'sort_on':'modified',
            'sort_order':'reverse',
        }
            
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
                        roles = api.user.get_roles(username=user.id, obj=obj)
                        with api.env.adopt_user(user=user):
                            if mtool.checkPermission('View', obj):
                                if (obj.observation_question_status() == 'phase1-pending-answer' \
                                    or obj.observation_question_status() == 'phase2-pending-answer') \
                                 and "MSExpert" in roles:
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

