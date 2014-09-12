from Acquisition import aq_parent
from DateTime import DateTime
from esdrt.content.observation import IObservation
from esdrt.content.question import IQuestion
from five import grok
from plone import api
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.utils import getToolByName


@grok.subscribe(IQuestion, IActionSucceededEvent)
def question_transition(question, event):
    if event.action == 'phase1-approve-question':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment.setEffectiveDate(DateTime())
            api.content.transition(obj=comment, transition='publish')
            return

    if event.action == 'phase1-recall-question-lr':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='retract')
            return

    if event.action == 'phase1-answer-to-lr':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            comment.setEffectiveDate(DateTime())
            api.content.transition(obj=comment, transition='publish')
            return

    if event.action == 'phase1-recall-msa':
        wf = getToolByName(question, 'portal_workflow')
        comment_id = wf.getInfoFor(question,
            'comments', wf_id='esd-question-review-workflow')
        comment = question.get(comment_id, None)
        if comment is not None:
            api.content.transition(obj=comment, transition='retract')
            return

    if api.content.get_state(obj=event.object) == 'phase1-closed':
        parent = aq_parent(event.object)
        with api.env.adopt_roles(roles=['Manager']):
            if api.content.get_state(parent) != 'phase1-conclusions':
                api.content.transition(obj=parent, transition='phase1-draft-conclusions')


@grok.subscribe(IObservation, IActionSucceededEvent)
def observation_transition(observation, event):
    if event.action == 'phase1-reopen':
        with api.env.adopt_roles(roles=['Manager']):
            qs = [q for q in observation.values() if q.portal_type == 'Question']
            if qs:
                q = qs[0]
                api.content.transition(obj=q, transition='phase1-reopen')

    elif event.action == 'phase1-request-comments':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='request-comments')

    elif event.action == 'phase1-finish-comments':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='redraft')

    elif event.action == 'phase1-request-close':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='publish')

    elif event.action == 'phase1-deny-closure':
        with api.env.adopt_roles(roles=['Manager']):
            conclusions = [c for c in observation.values() if c.portal_type == 'Conclusion']
            if conclusions:
                conclusion = conclusions[0]
                api.content.transition(obj=conclusion,
                    transition='redraft')

    elif event.action == 'phase1-draft-conclusions':
        with api.env.adopt_roles(roles=['Manager']):
            questions = [c for c in observation.values() if c.portal_type == 'Question']
            if questions:
                question = questions[0]
                if api.content.get_state(question) != 'phase1-closed':
                    api.content.transition(obj=question,
                        transition='phase1-close')