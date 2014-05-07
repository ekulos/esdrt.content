from esdrt.content.question import IQuestion
from five import grok
from plone import api
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName


@grok.subscribe(IQuestion, IActionSucceededEvent)
def question_transition(question, event):
    if event.action == 'approve-question':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='publish')

    if event.action == 'recall-question-lr':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='retract')

    if event.action == 'answer':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='publish')

    if event.action == 'recall-msa':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='retract')
