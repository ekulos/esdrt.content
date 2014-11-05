from Acquisition import aq_parent
from esdrt.content.question import IQuestion
from five import grok
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import PageTemplateFile
from utils import get_users_in_context
from utils import send_mail


@grok.subscribe(IQuestion, IActionSucceededEvent)
def notification_mse(context, event):
    """
    To:     MSExperts
    When:   New question for your country
    """
    _temp = PageTemplateFile('answer_to_msexperts.pt')

    if event.action in ['phase1-assign-answerer', 'phase2-assign-answerer']:
        observation = aq_parent(context)
        users = get_users_in_context(observation, roles=['MSExpert'])
        subject = u'New question for your country'
        content = _temp(**dict(observation=observation))
        send_mail(subject, safe_unicode(content), users)
