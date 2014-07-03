from Acquisition import aq_parent
from collective.contentrules.mailadapter.interfaces import IRecipientsResolver
from esdrt.content.observation import IObservation
from esdrt.content.question import PENDING_STATUS_NAME
from esdrt.content.question import OPEN_STATUS_NAME
from esdrt.content.question import DRAFT_STATUS_NAME
from esdrt.content.question import CLOSED_STATUS_NAME
from esdrt.content.question import IQuestion
from esdrt.content.subscriptions.interfaces import INotificationSubscriptions
from esdrt.content.subscriptions.interfaces import INotificationUnsubscriptions
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements


class NotificationReceivers(object):
    implements(IRecipientsResolver)
    adapts(IObservation)
    """ check the workflow history, get the usernames involved, and then
        the emails
    """
    def __init__(self, context):
        self.context = context

    def recipients(self):
        """ Recipients for an observation are:
            1. All users who have made an action on this item
            2. All users registered to receive notifications

            And we have to exclude:
            1. All users unsubscribed from receive notifications

        """
        context = self.context
        wtool = getToolByName(context, 'portal_workflow')
        actors = []

        # 1. Get all involved users
        with api.env.adopt_roles(['Manager']):
            info = wtool.getInfoFor(context, 'review_history',
                wf_id='esd-review-workflow'
            )
            actors = [inf['actor'] for inf in info]

        # 2. Explicit subscribed users
        actors.extend(INotificationSubscriptions(context).get())

        # 3. All users affected in the question
        with api.env.adopt_roles(['Manager']):
            for question in context.values():
                actors.extend(IRecipientsResolver(question).recipients())

        unsubscribed_users = INotificationUnsubscriptions(context).get()
        items = []
        putils = getToolByName(context, "plone_utils")
        for actor in set(actors):
            # 3. remove unsubsribed users
            if actor not in unsubscribed_users:
                user = api.user.get(username=actor)
                if user is not None:
                    email = user.getProperty('email')
                    if email and putils.validateSingleEmailAddress(email):
                        items.append(email)

        return items


class QuestionNotificationReceivers(object):
    implements(IRecipientsResolver)
    adapts(IQuestion)
    """ check the workflow history, get the usernames involved, and then
        the emails
    """
    def __init__(self, context):
        self.context = context

    def recipients(self):
        """ Recipients for an observation are:
            1. All users who have made an action on this item
            2. All users registered to receive notifications

            And we have to exclude:
            1. All users unsubscribed from receive notifications

        """
        context = self.context
        wtool = getToolByName(context, 'portal_workflow')
        actors = []
        last_actor = None

        # 0. Get groups users
        #   ReviewExperts
        #   LeadReviewers
        #   MSAuthority
        #   MSExperts
        country = context.country.lower()
        sector = context.ghg_source_sectors
        sre_groupname = 'extranet-esd-reviewexperts-%s-%s' % (sector, country)
        lr_groupname = 'extranet-esd-leadreviewers-%s' % country
        msa_groupname = 'extranet-esd-ms-authorities-%s' % country
        mse_groupname = 'extranet-esd-ms-experts-%s' % country

        sres = [u.getId() for u in api.user.get_users(groupname=sre_groupname)]
        lrs = [u.getId() for u in api.user.get_users(groupname=lr_groupname)]
        msas = [u.getId() for u in api.user.get_users(groupname=msa_groupname)]
        mses = [u.getId() for u in api.user.get_users(groupname=mse_groupname)]

        if context.get_status() in PENDING_STATUS_NAME:
            actors.extend(sres)
            actors.extend(lrs)
        elif context.get_status() in OPEN_STATUS_NAME:
            actors.extend(msas)
            if api.content.get_state(context) == 'pending-answer':
                actors.extend(mses)
        elif context.get_status() in DRAFT_STATUS_NAME:
            actors.extend(sres)
            actors.extend(lrs)
        elif context.get_status() in CLOSED_STATUS_NAME:
            actors.extend(lrs)
            actors.extend(msas)

        # 1. Remove the actor doing last change
        with api.env.adopt_roles(['Manager']):
            info = wtool.getInfoFor(context, 'review_history',
                wf_id='esd-question-review-workflow'
            )
            #actors = [inf['actor'] for inf in info]
            info.sort(lambda x, y: cmp(x['time'], y['time']))
            last_actor = info[-1].get('actor')

        # 2. Explicit subscribed users
        actors.extend(INotificationSubscriptions(context).get())

        unsubscribed_users = INotificationUnsubscriptions(context).get()
        items = []
        putils = getToolByName(context, "plone_utils")
        for actor in set(actors):
            # 3. remove unsubscribed users and the last actor
            if actor and \
                actor not in unsubscribed_users \
                    and actor != last_actor:
                user = api.user.get(username=actor)
                if user is not None:
                    email = user.getProperty('email')
                    if email and putils.validateSingleEmailAddress(email):
                        items.append(email)

        return items
