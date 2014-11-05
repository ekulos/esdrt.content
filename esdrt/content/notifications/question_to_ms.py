from Acquisition import aq_parent
from esdrt.content.question import IQuestion
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_ms(context, event):
    """
    To:     MSAuthority
    When:   New question for your country
    """
    _temp = PageTemplateFile('question_to_ms.pt')

    if event.action in ['phase1-approve-question', 'phase2-approve-question']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['MSAuthority'])
        subject = u'New question for your country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_rev_ph1(context, event):
    """
    To:     ReviewerPhase1
    When:   Your question was sent to MS
    """
    _temp = PageTemplateFile('question_to_ms_rev_msg.pt')

    if event.action in ['phase1-approve-question']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['ReviewerPhase1'])
        subject = u'Your observation was sent to MS'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_rev_ph2(context, event):
    """
    To:     ReviewerPhase2
    When:   Your question was sent to MS
    """
    _temp = PageTemplateFile('question_to_ms_rev_msg.pt')

    if event.action in ['phase2-approve-question']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['ReviewerPhase2'])
        subject = u'Your observation was sent to MS'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
