from esdrt.content.observation import IObservation
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_rev_ph1(context, event):
    """
    To:     ReviewerPhase1
    When:   Observation finalisation denied
    """
    _temp = PageTemplateFile('observation_finalisation_denied.pt')

    if event.action in ['phase1-deny-closure']:
        observation = context
        users = get_users_in_context(observation, roles=['ReviewerPhase1'])
        subject = u'Observation finalisation denied'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_rev_ph2(context, event):
    """
    To:     ReviewerPhase2
    When:   Observation finalisation denied
    """
    _temp = PageTemplateFile('observation_finalisation_denied.pt')

    if event.action in ['phase2-deny-finishing-observation']:
        observation = context
        users = get_users_in_context(observation, roles=['ReviewerPhase2'])
        subject = u'Observation finalisation denied'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
