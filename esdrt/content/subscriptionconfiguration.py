from plone import api
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from plone.memoize.view import memoize
from .observation import IObservation
from .observation import ObservationView
from esdrt.content.subscriptions.interfaces import INotificationUnsubscriptions
from esdrt.content.subscriptions.dexterity import UNSUBSCRIPTION_KEY
from BTrees.OOBTree import OOBTree
from zope.annotation.interfaces import IAnnotations

ROLE_TRANSLATOR = {
    'ReviewerPhase1': 'Sector Reviewer (phase 1)',
    'ReviewerPhase2': 'Review Expert (phase 2)',
    'QualityExpert':  'Quality Expert (phase 1)',
    'LeadReviewer':   'Lead Reviewer (phase 2)',
    'MSAuthority':    'Member State Coordinator',
    'CounterPart':    'Counter Part',
    'MSExpert':       'Member State Expert',
}


NOTIFICATIONS_PER_ROLE = {
    'ReviewerPhase1': {
        'observation_finalisation_denied': True,
        'observation_finalised': True,
        'question_answered': True,
        'question_to_ms': True,
    },
    'ReviewerPhase2': {
        'observation_finalisation_denied': True,
        'observation_finalised': True,
        'observation_to_phase2': True,
        'question_answered': True,
        'question_to_ms': True,
    },
    'QualityExpert': {
        'conclusion_to_comment': True,
        'observation_finalisation_request': True,
        'question_answered': True,
        'question_ready_for_approval': True,
        'question_to_counterpart': True,
    },
    'LeadReviewer': {
        'conclusion_to_comment': True,
        'observation_finalisation_request': True,
        'observation_to_phase2': True,
        'question_answered': True,
        'question_ready_for_approval': True,
        'question_to_counterpart': True,
    },
    'MSAuthority': {
        'answer_acknowledged': True,
        'observation_finalised': True,
        'question_to_ms': True,
    },
    'CounterPart': {
        'conclusion_to_comment': True,
        'question_to_counterpart': True,
    },
    'MSExpert': {
        'answer_to_msexperts': True,
        'question_answered': True,
    },
}

grok.templatedir('templates')


class SubscriptionConfiguration(ObservationView):
    grok.context(IObservation)
    grok.name('subscription-configuration')
    grok.require('zope2.View')

    @memoize
    def user(self):
        return api.user.get_current()

    def user_roles(self, translated_roles=True):
        user = self.user()
        roles = []
        for role in api.user.get_roles(user=user, obj=self.context):
            if translated_roles:
                translated = ROLE_TRANSLATOR.get(role)
                if translated is not None:
                    roles.append(translated)
            else:
                if role in ROLE_TRANSLATOR.keys():
                    roles.append(role)
        return roles

    def my_subscriptions(self):
        user = self.user()
        adapted = INotificationUnsubscriptions(self.context)
        unsubscribed_notifications = adapted.get_user_data(user.getId())
        roles = self.user_roles(translated_roles=False)
        items = {}
        for role in roles:
            data = NOTIFICATIONS_PER_ROLE.get(role)
            for unsubscribed in unsubscribed_notifications.get(role, []):
                data[unsubscribed] = False

            items[role] = data
        return items


class SaveSubscriptions(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')
    grok.name('save-subscriptions')

    @memoize
    def user(self):
        return api.user.get_current()

    def user_roles(self, translated_roles=True):
        user = self.user()
        roles = []
        for role in api.user.get_roles(user=user, obj=self.context):
            if translated_roles:
                translated = ROLE_TRANSLATOR.get(role)
                if translated is not None:
                    roles.append(translated)
            else:
                if role in ROLE_TRANSLATOR.keys():
                    roles.append(role)
        return roles

    def render(self):
        if self.request.get('REQUEST_METHOD') == 'POST':
            user = self.user()
            data = self.request.get('subscription_data')
            adapted = INotificationUnsubscriptions(self.context)
            user_roles = self.user_roles(translated_roles=False)
            to_delete = {}
            for item in data:
                copied_item = dict(item)
                rolename = copied_item.get('name')
                del copied_item['name']
                if rolename in user_roles:
                    notifications = set(NOTIFICATIONS_PER_ROLE.get(rolename))
                    deleted = notifications.difference(set(copied_item.keys()))
                    to_delete[rolename] = deleted

            adapted.unsubscribe(user.getId(), to_delete)
            status = IStatusMessage(self.request)
            status.add('Subscription preferences saved correctly', type='info')
            url = self.context.absolute_url() + '/subscription-configuration'
            return self.request.response.redirect(url)

        status = IStatusMessage(self.request)
        status.add('There was an error', type='error')
        return self.request.response.redirect(self.context.absolute_url())


class ClearSubscriptions(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')

    def render(self):
        adapted = IAnnotations(self.context)
        adapted[UNSUBSCRIPTION_KEY] = OOBTree()
        return 1