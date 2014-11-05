from esdrt.content.observation import IObservation
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_qe(context, event):
    """
    To:     QualityExpert
    When:   Observation finalisation request
    """
    _temp = PageTemplateFile('observation_finalisation_request.pt')

    if event.action in ['phase1-request-close']:
        observation = context
        users = get_users_in_context(observation, roles=['QualityExpert'])
        subject = u'Observation finalisation request'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   Observation finalisation request
    """
    _temp = PageTemplateFile('observation_finalisation_request.pt')

    if event.action in ['phase2-finish-observation']:
        observation = context
        users = get_users_in_context(observation, roles=['LeadReviewer'])
        subject = u'Observation finalisation request'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
