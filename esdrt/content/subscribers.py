from Acquisition import aq_parent
from DateTime import DateTime
from esdrt.content.conclusion import IConclusion
from esdrt.content.observation import IObservation
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
            comment.setEffectiveDate(DateTime())
            api.content.transition(obj=comment, transition='publish')
            return

    if event.action == 'recall-question-lr':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='retract')
            return

    if event.action == 'answer-to-lr':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment.setEffectiveDate(DateTime())
            api.content.transition(obj=comment, transition='publish')
            return

    if event.action == 'answer':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment.setEffectiveDate(DateTime())
            api.content.transition(obj=comment, transition='publish')
            return

    if event.action == 'recall-msa':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='retract')
            return

    if api.content.get_state(obj=event.object) == 'closed':
        parent = aq_parent(event.object)
        with api.env.adopt_roles(roles=['Manager']):
            api.content.transition(obj=parent, transition='draft-conclusions')


@grok.subscribe(IObservation, IActionSucceededEvent)
def observation_transition(observation, event):
    if event.action == 'reopen':
        with api.env.adopt_roles(roles=['Manager']):
            qs = [q for q in observation.values() if q.portal_type == 'Question']
            if qs:
                q = qs[0]
                api.content.transition(obj=q, transition='reopen')

    elif event.action == 'request-comments':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='request-comments')

    elif event.action == 'finish-comments':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='redraft')

    elif event.action == 'request-close':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='publish')

    elif event.action == 'deny-closure':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='redraft')