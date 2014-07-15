from plone.app.discussion.browser.comments import CommentForm as BaseForm
from plone.app.discussion.browser.comments import CommentsViewlet as BaseViewlet


class CommentForm(BaseForm):

    def updateActions(self):
        super(CommentForm, self).updateActions()
        self.actions['comment'].title = u'Save Comment'


class CommentsViewlet(BaseViewlet):
    form = CommentForm
