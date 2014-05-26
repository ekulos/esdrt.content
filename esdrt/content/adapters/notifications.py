from Acquisition import aq_parent
from collective.contentrules.mailadapter.interfaces import IRecipientsResolver
from esdrt.content.observation import IObservation
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
        # 1. Get all involved users
        with api.env.adopt_roles(['Manager']):
            info = wtool.getInfoFor(context, 'review_history',
                wf_id='esd-question-review-workflow'
            )
            actors = [inf['actor'] for inf in info]

        # 2. Explicit subscribed users
        actors.extend(INotificationSubscriptions(context).get())

        unsubscribed_users = INotificationUnsubscriptions(context).get()
        items = []
        putils = getToolByName(context, "plone_utils")
        for actor in set(actors):
            # 3. remove unsubsribed users
            if actor and actor not in unsubscribed_users:
                user = api.user.get(username=actor)
                if user is not None:
                    email = user.getProperty('email')
                    if email and putils.validateSingleEmailAddress(email):
                        items.append(email)

        return items
