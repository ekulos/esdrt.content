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
    When:   Answer Acknowledged
    """
    _temp = PageTemplateFile('answer_acknowledged.pt')

    if event.action in ['phase1-validate-answer-msa', 'phase2-validate-answer-msa']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['MSAuthority'])
        subject = u'Your answer was acknowledged'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
