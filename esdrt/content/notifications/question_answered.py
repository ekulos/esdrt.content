from Acquisition import aq_parent
from esdrt.content.question import IQuestion
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_qe(context, event):
    """
    To:     QualityExpert
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_lr_msg.pt')

    if event.action in ['phase1-answer-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['QualityExpert'])
        subject = u'New answer from country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_lr_msg.pt')

    if event.action in ['phase2-answer-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['LeadReviewer'])
        subject = u'New answer from country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_rev_ph1(context, event):
    """
    To:     ReviewerPhase1
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_rev_msg.pt')

    if event.action in ['phase1-answer-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['ReviewerPhase1'])
        subject = u'New answer from country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_rev_ph2(context, event):
    """
    To:     ReviewerPhase2
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_rev_msg.pt')

    if event.action in ['phase2-answer-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['ReviewerPhase2'])
        subject = u'New answer from country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_rev_msexperts(context, event):
    """
    To:     MSExperts
    When:   New answer from country
    """
    _temp = PageTemplateFile('question_answered_msexperts_msg.pt')

    if event.action in ['phase1-answer-to-lr', 'phase2-answer-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['MSExpert'])
        subject = u'New answer from country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
