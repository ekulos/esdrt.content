from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOSet


SUBSCRIPTION_KEY = 'esdrt.content.subscriptions.subscribed'
UNSUBSCRIPTION_KEY = 'esdrt.content.subscriptions.unsubscribed'


class NotificationSubscriptions(object):

    def __init__(self, context):
        self.context = context

    def get(self):
        annotated = IAnnotations(self.context)
        return list(annotated.get(SUBSCRIPTION_KEY, OOSet()))

    def add_notifications(self, userid):
        annotated = IAnnotations(self.context)
        data = annotated.get(SUBSCRIPTION_KEY, OOSet())
        if data.add(userid):
            annotated[SUBSCRIPTION_KEY] = data
            return 1
        return 0

    def del_notifications(self, userid):
        annotated = IAnnotations(self.context)
        data = annotated.get(SUBSCRIPTION_KEY, OOSet())
        try:
            data.remove(userid)
            annotated[SUBSCRIPTION_KEY] = data
            return 1
        except KeyError:
            return 0

        return 0


class NotificationUnsubscriptions(object):

    def __init__(self, context):
        self.context = context

    def get(self):
        annotated = IAnnotations(self.context)
        return list(annotated.get(UNSUBSCRIPTION_KEY, OOSet()))

    def unsubscribe(self, userid):
        annotated = IAnnotations(self.context)
        data = annotated.get(UNSUBSCRIPTION_KEY, OOSet())
        if data.add(userid):
            annotated[UNSUBSCRIPTION_KEY] = data
            return 1
        return 0

    def delete_unsubscribe(self, userid):
        annotated = IAnnotations(self.context)
        data = annotated.get(UNSUBSCRIPTION_KEY, OOSet())
        try:
            data.remove(userid)
            annotated[UNSUBSCRIPTION_KEY] = data
            return 1
        except KeyError:
            return 0
        return 0
