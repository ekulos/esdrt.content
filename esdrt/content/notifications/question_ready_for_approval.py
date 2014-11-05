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
    When:   New question for approval
    """
    _temp = PageTemplateFile('question_ready_for_approval.pt')

    if event.action in ['phase1-send-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['QualityExpert'])
        subject = u'New question for approval'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_lr(context, event):
    """
    To:     LeadReviewer
    When:   New question for approval
    """
    _temp = PageTemplateFile('question_ready_for_approval.pt')

    if event.action in ['phase2-send-to-lr']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['LeadReviewer'])
        subject = u'New question for approval'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
