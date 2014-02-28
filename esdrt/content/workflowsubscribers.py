from Acquisition import aq_inner
from Acquisition import aq_parent
from esdrt.content.comment import IComment
from esdrt.content.commentanswer import ICommentAnswer
from five import grok
from plone import api
from Products.CMFCore.interfaces import IActionSucceededEvent


@grok.subscribe(IComment, IActionSucceededEvent)
def publish_comment_after_sending_question(object, event):
    """
    We are using a two-state workflow for comments.
    Publish the comment when the Expert Reviewer has
    sent the comment to validation to the Lead Reviewer
    """
    comment = aq_inner(object)
    question = aq_parent(comment)
    if api.content.get_state(question) == 'published':
        api.content.transition(question, 'ask-question-approval')

    if api.content.get_state(question) == 'private':
        api.content.transition(question, 'redraft')


@grok.subscribe(ICommentAnswer, IActionSucceededEvent)
def publish_answer_after_sending_question(object, event):
    """
    We are using a two-state workflow for answer.
    Publish the comment when the Expert Reviewer has
    sent the comment to validation to the MS Authority
    """
    comment = aq_inner(object)
    question = aq_parent(comment)
    if api.content.get_state(question) == 'published':
        api.content.transition(question, 'ask-question-approval')

    if api.content.get_state(question) == 'private':
        api.content.transition(question, 'redraft')
