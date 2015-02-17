from esdrt.content.timeit import timeit
from AccessControl import getSecurityManager
from five import grok
from plone import api
from plone.directives import dexterity
from plone.directives import form
from plone.memoize import ram
from plone.memoize.view import memoize
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName
from eea.cache import cache



grok.templatedir('templates')


class IReviewFolder(form.Schema, IImageScaleTraversable):
    """
    Folder to have all observations together
    """


class ReviewFolder(dexterity.Container):
    grok.implements(IReviewFolder)


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
            'path': path,
            'portal_type': ['Observation', 'Question'],
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if (country != ""):
            query['Country'] = country
        if (status != ""):
            if status == "finished":
                query['review_state'] = [
                    'phase1-closed',
                    'phase2-closed'
                ]
            # if status == "draft":
            #     query['review_state'] = [
            #         'phase1-draft',
            #         'phase2-draft'
            #     ]
            # elif status == "conclusion-1":
            #     query['review_state'] = [
            #         'phase1-conclusions',
            #         'phase1-conclusion-discussion'
            #     ]
            # elif status == "conclusion-2":
            #     query['review_state'] = [
            #         'phase2-conclusions',
            #         'phase2-conclusion-discussion'
            #     ]
            else:
                query['review_state'] = [
                    'phase1-pending',
                    'phase2-pending',
                    'phase1-close-requested',
                    'phase2-close-requested',
                    'phase1-draft',
                    'phase2-draft',
                    'phase1-conclusions',
                    'phase1-conclusion-discussion',
                    'phase2-conclusions',
                    'phase2-conclusion-discussion',
                ]

        if reviewYear != "":
            query['review_year'] = reviewYear
        if inventoryYear != "":
            query['year'] = inventoryYear
        if highlights != "":
            query['highlight'] = highlights.split(",")
        if freeText != "":
            query['SearchableText'] = freeText

        return [b.getObject() for b in catalog(query)]

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
        review_years = [c for c in catalog.uniqueValuesFor('review_year') if isinstance(c, basestring)]
        return review_years

    def get_inventory_years(self):
        catalog = api.portal.get_tool('portal_catalog')
        inventory_years = catalog.uniqueValuesFor('year')
        return inventory_years


def _item_user(fun, self, user, item):
    return (user.getId(), item.getId(), item.modified())


def decorate(item):
    """ prepare a plain object, so that we can cache it in a RAM cache """
    user = api.user.get_current()
    roles = api.user.get_roles(username=user.getId(), obj=item, inherit=False)
    new_item = {}
    new_item['absolute_url'] = item.absolute_url()
    new_item['observation_css_class'] = item.observation_css_class()
    new_item['getId'] = item.getId()
    new_item['Title'] = item.Title()
    new_item['observation_is_potential_significant_issue'] = item.observation_is_potential_significant_issue()
    new_item['observation_is_potential_technical_correction'] = item.observation_is_potential_technical_correction()
    new_item['observation_is_technical_correction'] = item.observation_is_technical_correction()
    new_item['text'] = item.text
    new_item['crf_code_value'] = item.crf_code_value()
    new_item['modified'] = item.modified()
    new_item['observation_phase'] = item.observation_phase()
    new_item['observation_question_status'] = item.observation_question_status()
    new_item['last_answer_reply_number'] = item.last_answer_reply_number()
    new_item['get_status'] = item.get_status()
    new_item['observation_already_replied'] = item.observation_already_replied()
    new_item['reply_comments_by_mse'] = item.reply_comments_by_mse()
    new_item['observation_finalisation_reason'] = item.observation_finalisation_reason()
    new_item['isCP'] = 'CounterPart' in roles
    new_item['isMSA'] = 'MSAuthority' in roles
    return new_item


def _catalog_change(fun, self, *args, **kwargs):
    counter = api.portal.get_tool('portal_catalog').getCounter()
    user = api.user.get_current().getId()
    path = '/'.join(self.context.getPhysicalPath())
    return (counter, user, path)


class Inbox2ReviewFolderView(grok.View):
    grok.context(IReviewFolder)
    grok.require('zope2.View')
    grok.name('inboxview2')

    def update(self):
        freeText = self.request.form.get('freeText', '')
        self.observations = self.get_all_observations(freeText)

    @cache(_catalog_change)
    @timeit
    def get_all_observations(self, freeText):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': 'Observation',
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if freeText != "":
            query['SearchableText'] = freeText

        return map(decorate, [b.getObject() for b in catalog.searchResults(query)])

    """
        Sector expert / Review expert
    """



    def get_draft_observations(self):
        """
         Role: Sector expert / Review expert
         without actions for LR, counterpart or MS
        """
        items = []
        for item in self.observations:
            if item.get('observation_question_status', '') in [
                    'observation-phase1-draft',
                    'observation-phase2-draft']:
                items.append(item)
        return items



    def get_draft_questions(self):
        """
         Role: Sector expert / Review expert
         with comments from counterpart or LR
        """
        items = []
        for item in self.observations:
            if item.get('observation_question_status', '') in [
                    'phase1-draft',
                    'phase2-draft',
                    'phase1-counterpart-comments',
                    'phase2-counterpart-comments']:
                items.append(item)
        return items

    @ram.cache(_item_user)
    def get_roles_for_item(self, user, item):
        return api.user.get_roles(username=user.id, obj=item, inherit=False)



    def get_counterpart_questions_to_comment(self):
        """
         Role: Sector expert / Review expert
         needing comment from me
        """
        items = []
        for item in self.observations:
            # roles = self.get_roles_for_item(user, item)
            if item.get('observation_question_status', '') in [
                    'phase1-counterpart-comments',
                    'phase2-counterpart-comments'] and \
                    item.get('isCP', ''):
                items.append(item)
        return items



    def get_counterpart_conclusion_to_comment(self):
        """
         Role: Sector expert / Review expert
         needing comment from me
        """
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-conclusion-discussion',
                    'phase2-conclusion-discussion'] and \
                    obj.get('isCP', ''):
                items.append(item)
        return items



    def get_ms_answers_to_review(self):
        """
         Role: Sector expert / Review expert
         that need review
        """
        # user = api.user.get_current()
        # mtool = api.portal.get_tool('portal_membership')
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-answered',
                    'phase2-answered',
                    ] or \
                    (obj.get('get_status') in [
                        'phase1-pending',
                        'phase2-pending',
                        ] and \
                    obj.get('observation_question_status', '') in [
                        'phase1-closed',
                        'phase2-closed',
                    ]):
                items.append(obj)
        return items



    def get_unanswered_questions(self):
        """
         Role: Sector expert / Review expert
         my questions sent to LR and MS and waiting for reply
        """
        items = []

        statuses = [
            'phase1-pending',
            'phase2-pending',
            'phase1-recalled-msa',
            'phase2-recalled-msa',
            'phase1-expert-comments',
            'phase2-expert-comments',
            'phase1-pending-answer-drafting',
            'phase2-pending-answer-drafting'
        ]

        # For a SE/RE, those on QE/LR pending to be sent to the MS
        # or recalled by him, are unanswered questions
        if self.is_sector_expert_or_review_expert():
            statuses.extend([
                'phase1-drafted',
                'phase2-drafted',
                'phase1-recalled-lr',
                'phase2-recalled-lr']
            )

        for obj in self.observations:
            if obj.get('observation_question_status', '') in statuses:
                items.append(obj)
        return items



    def get_waiting_for_comment_from_counterparts_for_question(self):
        """
         Role: Sector expert / Review expert
        """
        # user = api.user.get_current()
        # mtool = api.portal.get_tool('portal_membership')
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-counterpart-comments',
                    'phase2-counterpart-comments'] and \
                    obj.get('isCP', ''):
                items.append(obj)
        return items



    def get_waiting_for_comment_from_counterparts_for_conclusion(self):
        """
         Role: Sector expert / Review expert
        """
        # user = api.user.get_current()
        # mtool = api.portal.get_tool('portal_membership')
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-conclusion-discussion',
                    'phase2-conclusion-discussion'] and \
                    obj.get('isCP', ''):
                items.append(obj)
        return items



    def get_observation_for_finalisation(self):
        """
         Role: Sector expert / Review expert
         waiting approval from LR
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-conclusions',
                    'phase2-conclusions',
                    'phase1-close-requested',
                    'phase2-close-requested',]:
                items.append(obj)
        return items

    """
        Lead Reviewer / Quality expert
    """


    def get_questions_to_be_sent(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for me to send to the MS
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-drafted',
                    'phase2-drafted',
                    'phase1-recalled-lr',
                    'phase2-recalled-lr']:
                items.append(obj)
        return items



    def get_observations_to_finalise(self):
        """
         Role: Lead Reviewer / Quality expert
         Observations waiting for me to confirm finalisation
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-close-requested',
                    'phase2-close-requested']:
                items.append(obj)
        return items



    def get_questions_to_comment(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for my comments
        """
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-counterpart-comments',
                    'phase2-counterpart-comments'] and \
                    obj.get('isCP', ''):
                items.append(obj)
        return items



    def get_conclusions_to_comment(self):
        """
         Role: Lead Reviewer / Quality expert
         Conclusions waiting for my comments
        """
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-conclusion-discussion',
                    'phase2-conclusion-discussion'] and \
                    obj.get('isCP', ''):
                items.append(obj)
        return items



    def get_questions_with_comments_from_reviewers(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for comments by counterpart
        """
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-counterpart-comments',
                    'phase2-counterpart-comments'] and \
                    obj.get('isCP', ''):
                items.append(obj)
        return items



    def get_answers_from_ms(self):
        """
         Role: Lead Reviewer / Quality expert
         that need review by Sector Expert/Review expert
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-answered',
                    'phase2-answered']:
                items.append(obj)
        return items



    def get_unanswered_questions_lr_qe(self):
        """
         Role: Lead Reviewer / Quality expert
         questions waiting for comments from MS
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-pending',
                    'phase2-pending',
                    'phase1-recalled-msa',
                    'phase2-recalled-msa',
                    'phase1-expert-comments',
                    'phase2-expert-comments',
                    'phase1-pending-answer-drafting',
                    'phase2-pending-answer-drafting']:
                items.append(obj)
        return items

    """
        MS Coordinator
    """


    def get_questions_to_be_answered(self):
        """
         Role: MS Coordinator
         Questions from the SE/RE to be answered
        """
        items = []
        for obj in self.observations:
            # roles = self.get_roles_for_item(user, obj)
            if obj.get('observation_question_status', '') in [
                    'phase1-pending',
                    'phase2-pending',
                    'phase1-recalled-msa',
                    'phase2-recalled-msa',
                    'phase1-pending-answer-drafting',
                    'phase2-pending-answer-drafting'] and obj.get('isMSA', ''):
                items.append(obj)
        return items



    def get_questions_with_comments_received_from_mse(self):
        """
         Role: MS Coordinator
         Comments received from MS Experts
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-expert-comments',
                    'phase2-expert-comments'] and \
                    obj.get('last_answer_reply_number') > 0:
                items.append(obj)
        return items



    def get_answers_requiring_comments_from_mse(self):
        """
         Role: MS Coordinator
         Answers requiring comments/discussion from MS experts
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-expert-comments',
                    'phase2-expert-comments']:
                items.append(obj)
        return items



    def get_answers_sent_to_se_re(self):
        """
         Role: MS Coordinator
         Answers sent to SE/RE
        """
        items = []
        for obj in self.observations:
            if (obj.get('observation_question_status', '') in [
                    'phase1-answered', 'phase2-answered'] or \
                    obj.get('observation_already_replied')) and \
                    obj.get('get_status', '') not in [
                        'phase1-closed',
                        'phase2-closed']:
                items.append(obj)
        return items
    """
        MS Expert
    """


    def get_questions_with_comments_for_answer_needed_by_msc(self):
        """
         Role: MS Expert
         Comments for answer needed by MS Coordinator
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-expert-comments',
                    'phase2-expert-comments']:
                items.append(obj)
        return items



    def get_observations_with_my_comments(self):
        """
         Role: MS Expert
         Observation I have commented on
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-expert-comments',
                    'phase2-expert-comments',
                    'phase1-pending-answer-drafting',
                    'phase2-pending-answer-drafting'] and \
                    obj.get('reply_comments_by_mse'):
                items.append(obj)
        return items



    def get_observations_with_my_comments_sent_to_se_re(self):
        """
         Role: MS Expert
         Answers that I commented on sent to Sector Expert/Review expert
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-answered',
                    'phase2-answered',
                    'phase1-recalled-msa',
                    'phase2-recalled-msa'] and \
                    obj.get('reply_comments_by_mse'):
                items.append(obj)
        return items

    """
        Finalised observations
    """


    def get_no_response_needed_observations(self):
        """
         Finalised with 'no response needed'
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-closed',
                    'phase2-closed'] and \
                    obj.get('observation_finalisation_reason', '') == 'no-response-needed':
                items.append(obj)
        return items



    def get_resolved_observations(self):
        """
         Finalised with 'resolved'
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-closed',
                    'phase2-closed'] and \
                    obj.get('observation_finalisation_reason', '') == 'resolved':
                items.append(obj)
        return items



    def get_unresolved_observations(self):
        """
         Finalised with 'unresolved'
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-closed',
                    'phase2-closed'] and \
                    obj.get('observation_finalisation_reason', '') == 'unresolved':
                items.append(obj)
        return items



    def get_partly_resolved_observations(self):
        """
         Finalised with 'partly resolved'
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-closed',
                    'phase2-closed'] and \
                    obj.get('observation_finalisation_reason', '') == 'partly-resolved':
                items.append(obj)
        return items



    def get_technical_correction_observations(self):
        """
         Finalised with 'technical correction'
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-closed',
                    'phase2-closed'] and \
                    obj.get('observation_finalisation_reason', '') == 'technical-correction':
                items.append(obj)
        return items



    def get_revised_estimate_observations(self):
        """
         Finalised with 'partly resolved'
        """
        items = []
        for obj in self.observations:
            if obj.get('observation_question_status', '') in [
                    'phase1-closed',
                    'phase2-closed'] and \
                    obj.get('observation_finalisation_reason', '') == 'revised-estimate':
                items.append(obj)
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

    def is_sector_expert_or_review_expert(self):
        user = api.user.get_current()
        user_groups = user.getGroups()
        is_se = 'extranet-esd-ghginv-sr' in user_groups
        is_re = 'extranet-esd-esdreview-reviewexp' in user_groups
        return is_se or is_re

    def is_lead_reviewer_or_quality_expert(self):
        user = api.user.get_current()
        user_groups = user.getGroups()
        is_qe = 'extranet-esd-ghginv-qualityexpert' in user_groups
        is_lr = 'extranet-esd-esdreview-leadreview' in user_groups
        return is_qe or is_lr

    def is_member_state_coordinator(self):
        user = api.user.get_current()
        return "extranet-esd-countries-msa" in user.getGroups()

    def is_member_state_expert(self):
        user = api.user.get_current()
        return "extranet-esd-countries-msexpert" in user.getGroups()


class InboxReviewFolderView(grok.View):
    grok.context(IReviewFolder)
    grok.require('zope2.View')
    grok.name('inboxview4')

    def can_add_observation(self):
        sm = getSecurityManager()
        return sm.checkPermission('esdrt.content: Add Observation', self)


def decorate2(item):
    """ prepare a plain object, so that we can cache it in a RAM cache """
    user = api.user.get_current()
    roles = api.user.get_roles(username=user.getId(), obj=item, inherit=True)
    item.isCP = 'CounterPart' in roles
    item.isMSA = 'MSAuthority' in roles
    return item


class Inbox3ReviewFolderView(grok.View):
    grok.context(IReviewFolder)
    grok.require('zope2.View')
    grok.name('inboxview')

    @cache(_catalog_change)
    @timeit
    def get_all_observations(self, freeText):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': 'Observation',
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if freeText != "":
            query['SearchableText'] = freeText

        return map(decorate, [b.getObject() for b in catalog.searchResults(query)])

    def get_observations(self, freeText=None, rolecheck=None, **kw):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        query = {
            'path': path,
            'portal_type': 'Observation',
            'sort_on': 'modified',
            'sort_order': 'reverse',
        }
        if freeText:
            query['SearchableText'] = freeText

        query.update(kw)

        from logging import getLogger
        log = getLogger(__name__)
        if rolecheck is None:
            log.info('Querying Catalog: %s' % query)
            return [b.getObject() for b in catalog.searchResults(query)]
        else:
            log.info('Querying Catalog with Rolecheck %s: %s ' % (rolecheck, query))

            def makefilter(rolename):
                """
                https://stackoverflow.com/questions/7045754/python-list-filtering-with-arguments
                """
                def myfilter(x):
                    if rolename == 'CounterPart':
                        return x.isCP
                    elif rolename == 'MSAuthority':
                        return x.isMSA
                    return False
                return myfilter

            filterfunc = makefilter(rolecheck)

            return filter(
                filterfunc,
                map(decorate2,
                    [b.getObject() for b in catalog.searchResults(query)])
            )

    @timeit
    def get_draft_observations(self):
        """
         Role: Sector expert / Review expert
         without actions for LR, counterpart or MS
        """
        return self.get_observations(
            observation_question_status=[
                'observation-phase1-draft', 'observation-phase2-draft'])

    @timeit
    def get_draft_questions(self):
        """
         Role: Sector expert / Review expert
         with comments from counterpart or LR
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-draft',
                'phase2-draft',
                'phase1-counterpart-comments',
                'phase2-counterpart-comments'])

    @timeit
    def get_counterpart_questions_to_comment(self):
        """
         Role: Sector expert / Review expert
         needing comment from me
        """
        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-counterpart-comments',
                'phase2-counterpart-comments'])

    @timeit
    def get_counterpart_conclusion_to_comment(self):
        """
         Role: Sector expert / Review expert
         needing comment from me
        """
        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-conclusion-discussion',
                'phase2-conclusion-discussion'])

    @timeit
    def get_ms_answers_to_review(self):
        """
         Role: Sector expert / Review expert
         that need review
        """
        # user = api.user.get_current()
        # mtool = api.portal.get_tool('portal_membership')

        answered = self.get_observations(
            observation_question_status=[
                'phase1-answered',
                'phase2-answered'])

        pending = self.get_observations(
            observation_question_status=['phase1-closed', 'phase2-closed'],
            review_state=['phase1-pending', 'phase2-pending'])

        return answered + pending

    @timeit
    def get_unanswered_questions(self):
        """
         Role: Sector expert / Review expert
         my questions sent to LR and MS and waiting for reply
        """
        statuses = [
            'phase1-pending',
            'phase2-pending',
            'phase1-recalled-msa',
            'phase2-recalled-msa',
            'phase1-expert-comments',
            'phase2-expert-comments',
            'phase1-pending-answer-drafting',
            'phase2-pending-answer-drafting'
        ]

        # For a SE/RE, those on QE/LR pending to be sent to the MS
        # or recalled by him, are unanswered questions
        if self.is_sector_expert_or_review_expert():
            statuses.extend([
                'phase1-drafted',
                'phase2-drafted',
                'phase1-recalled-lr',
                'phase2-recalled-lr']
            )

        return self.get_observations(observation_question_status=statuses)

    @timeit
    def get_waiting_for_comment_from_counterparts_for_question(self):
        """
         Role: Sector expert / Review expert
        """

        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-counterpart-comments',
                'phase2-counterpart-comments'])

    @timeit
    def get_waiting_for_comment_from_counterparts_for_conclusion(self):
        """
         Role: Sector expert / Review expert
        """
        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-conclusion-discussion',
                'phase2-conclusion-discussion'])

    @timeit
    def get_observation_for_finalisation(self):
        """
         Role: Sector expert / Review expert
         waiting approval from LR
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-conclusions',
                'phase2-conclusions',
                'phase1-close-requested',
                'phase2-close-requested'])

    """
        Lead Reviewer / Quality expert
    """
    @timeit
    def get_questions_to_be_sent(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for me to send to the MS
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-drafted',
                'phase2-drafted',
                'phase1-recalled-lr',
                'phase2-recalled-lr'])

    @timeit
    def get_observations_to_finalise(self):
        """
         Role: Lead Reviewer / Quality expert
         Observations waiting for me to confirm finalisation
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-close-requested',
                'phase2-close-requested'])

    @timeit
    def get_questions_to_comment(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for my comments
        """
        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-counterpart-comments',
                'phase2-counterpart-comments'])

    @timeit
    def get_conclusions_to_comment(self):
        """
         Role: Lead Reviewer / Quality expert
         Conclusions waiting for my comments
        """
        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-conclusion-discussion',
                'phase2-conclusion-discussion'])

    @timeit
    def get_questions_with_comments_from_reviewers(self):
        """
         Role: Lead Reviewer / Quality expert
         Questions waiting for comments by counterpart
        """
        return self.get_observations(
            rolecheck='CounterPart',
            observation_question_status=[
                'phase1-counterpart-comments',
                'phase2-counterpart-comments'])

    @timeit
    def get_answers_from_ms(self):
        """
         Role: Lead Reviewer / Quality expert
         that need review by Sector Expert/Review expert
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-answered',
                'phase2-answered'])

    @timeit
    def get_unanswered_questions_lr_qe(self):
        """
         Role: Lead Reviewer / Quality expert
         questions waiting for comments from MS
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-pending',
                'phase2-pending',
                'phase1-recalled-msa',
                'phase2-recalled-msa',
                'phase1-expert-comments',
                'phase2-expert-comments',
                'phase1-pending-answer-drafting',
                'phase2-pending-answer-drafting'])

    """
        MS Coordinator
    """
    @timeit
    def get_questions_to_be_answered(self):
        """
         Role: MS Coordinator
         Questions from the SE/RE to be answered
        """
        return self.get_observations(
            rolecheck='MSAuthority',
            observation_question_status=[
                'phase1-pending',
                'phase2-pending',
                'phase1-recalled-msa',
                'phase2-recalled-msa',
                'phase1-pending-answer-drafting',
                'phase2-pending-answer-drafting'])

    @timeit
    def get_questions_with_comments_received_from_mse(self):
        """
         Role: MS Coordinator
         Comments received from MS Experts
        """
        return self.get_observations(
            rolecheck='MSAuthority',
            observation_question_status=[
                'phase1-expert-comments',
                'phase2-expert-comments'],
            last_answer_has_replies=True,
            # last_answer_reply_number > 0
        )

    @timeit
    def get_answers_requiring_comments_from_mse(self):
        """
         Role: MS Coordinator
         Answers requiring comments/discussion from MS experts
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-expert-comments',
                'phase2-expert-comments'],
        )

    @timeit
    def get_answers_sent_to_se_re(self):
        """
         Role: MS Coordinator
         Answers sent to SE/RE
        """
        answered = self.get_observations(
            observation_question_status=['phase1-answered', 'phase2-answered'])
        cat = api.portal.get_tool('portal_catalog')
        statuses = list(cat.uniqueValuesFor('review_state'))
        try:
            statuses.remove('phase1-closed')
        except ValueError:
            pass
        try:
            statuses.remove('phase2-closed')
        except ValueError:
            pass
        not_closed = self.get_observations(
            review_state=statuses,
            observation_already_replied=True)

        return set(answered + not_closed)

    """
        MS Expert
    """
    @timeit
    def get_questions_with_comments_for_answer_needed_by_msc(self):
        """
         Role: MS Expert
         Comments for answer needed by MS Coordinator
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-expert-comments',
                'phase2-expert-comments'])

    @timeit
    def get_observations_with_my_comments(self):
        """
         Role: MS Expert
         Observation I have commented on
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-expert-comments',
                'phase2-expert-comments',
                'phase1-pending-answer-drafting',
                'phase2-pending-answer-drafting'],
            reply_comments_by_mse=True,
        )

    @timeit
    def get_observations_with_my_comments_sent_to_se_re(self):
        """
         Role: MS Expert
         Answers that I commented on sent to Sector Expert/Review expert
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-answered',
                'phase2-answered',
                'phase1-recalled-msa',
                'phase2-recalled-msa'],
            reply_comments_by_mse=True,
        )

    """
        Finalised observations
    """
    @timeit
    def get_no_response_needed_observations(self):
        """
         Finalised with 'no response needed'
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-closed',
                'phase2-closed'],
            observation_finalisation_reason='no-response-needed',
        )

    @timeit
    def get_resolved_observations(self):
        """
         Finalised with 'resolved'
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-closed',
                'phase2-closed'],
            observation_finalisation_reason='resolved',
        )

    @timeit
    def get_unresolved_observations(self):
        """
         Finalised with 'unresolved'
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-closed',
                'phase2-closed'],
            observation_finalisation_reason='unresolved',
        )

    @timeit
    def get_partly_resolved_observations(self):
        """
         Finalised with 'partly resolved'
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-closed',
                'phase2-closed'],
            observation_finalisation_reason='partly-resolved',
        )

    @timeit
    def get_technical_correction_observations(self):
        """
         Finalised with 'technical correction'
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-closed',
                'phase2-closed'],
            observation_finalisation_reason='technical-correction',
        )

    @timeit
    def get_revised_estimate_observations(self):
        """
         Finalised with 'partly resolved'
        """
        return self.get_observations(
            observation_question_status=[
                'phase1-closed',
                'phase2-closed'],
            observation_finalisation_reason='revised-estimate',
        )

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

    def is_sector_expert_or_review_expert(self):
        user = api.user.get_current()
        user_groups = user.getGroups()
        is_se = 'extranet-esd-ghginv-sr' in user_groups
        is_re = 'extranet-esd-esdreview-reviewexp' in user_groups
        return is_se or is_re

    def is_lead_reviewer_or_quality_expert(self):
        user = api.user.get_current()
        user_groups = user.getGroups()
        is_qe = 'extranet-esd-ghginv-qualityexpert' in user_groups
        is_lr = 'extranet-esd-esdreview-leadreview' in user_groups
        return is_qe or is_lr

    def is_member_state_coordinator(self):
        user = api.user.get_current()
        return "extranet-esd-countries-msa" in user.getGroups()

    def is_member_state_expert(self):
        user = api.user.get_current()
        return "extranet-esd-countries-msexpert" in user.getGroups()


class FirstObservation(Inbox3ReviewFolderView):
    grok.context(IReviewFolder)
    grok.name('get-first-reviewable-observation')
    grok.require('zope2.View')

    def update(self):
        super(FirstObservation, self).update()
        url = ''
        obs = self.get_draft_observations()
        if obs:
            url = obs[0].absolute_url()

        return self.request.response.redirect(url)

    def render(self):
        return ''
