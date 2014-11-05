from Acquisition import aq_parent
from esdrt.content.observation import IObservation
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_cp(context, event):
    """
    To:     CounterParts
    When:   New draft conclusion to comment on
    """
    _temp = PageTemplateFile('conclusion_to_comment.pt')

    if event.action in ['phase1-request-comments', 'phase2-request-comments']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['CounterPart'])
        subject = u'New draft conclusion to comment on'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_qe(context, event):
    """
    To:     QualityExpert
    When:   New draft conclusion to comment on
    """
    _temp = PageTemplateFile('conclusion_to_comment.pt')

    if event.action in ['phase1-request-comments']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['QualityExpert'])
        subject = u'New draft conclusion to comment on'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IObservation, IActionSucceededEvent)
def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New draft question to comment on
    """
    _temp = PageTemplateFile('conclusion_to_comment.pt')

    if event.action in ['phase2-request-comments']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['LeadReviewer'])
        subject = u'New draft conclusion to comment on'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
