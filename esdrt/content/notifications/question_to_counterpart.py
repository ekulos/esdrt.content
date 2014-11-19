from Acquisition import aq_parent
from esdrt.content.question import IQuestion
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail
from utils import notify


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_cp(context, event):
    """
    To:     CounterParts
    When:   New draft question to comment on
    """
    _temp = PageTemplateFile('question_to_counterpart.pt')

    if event.action in ['phase1-request-for-counterpart-comments', 'phase2-request-for-counterpart-comments']:
        observation = aq_parent(context)
        subject = u'New draft question to comment'
        notify(observation, _temp, subject, roles=['CounterPart'])


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_qe(context, event):
    """
    To:     QualityExpert
    When:   New draft question to comment on
    """
    _temp = PageTemplateFile('question_to_counterpart.pt')

    if event.action in ['phase1-request-for-counterpart-comments']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['QualityExpert'])
        subject = u'New draft question to comment'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New draft question to comment on
    """
    _temp = PageTemplateFile('question_to_counterpart.pt')

    if event.action in ['phase2-request-for-counterpart-comments']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['LeadReviewer'])
        subject = u'New draft question to comment'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)