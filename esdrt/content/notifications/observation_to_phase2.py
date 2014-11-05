from esdrt.content.observation import IObservation
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   Observation handed over to phase 2
    """
    _temp = PageTemplateFile('observation_to_phase2.pt')

    if event.action in ['phase1-send-to-team-2']:
        observation = context
        users = get_users_in_context(observation, roles=['LeadReviewer'])
        subject = u'Observation handed over to phase 2'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_rev_ph2(context, event):
    """
    To:     ReviewerPhase2
    When:   Observation handed over to phase 2
    """
    _temp = PageTemplateFile('observation_to_phase2_rev_msg.pt')

    if event.action in ['phase1-send-to-team-2']:
        observation = context
        users = get_users_in_context(observation, roles=['ReviewerPhase2'])
        subject = u'Observation handed over to phase 2'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
