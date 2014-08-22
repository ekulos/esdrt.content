from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.discussion.interfaces import IComment
from five import grok


class CopyFileToAnswer(grok.View):
    grok.require('esdrt.content.AddESDRTFile')
    grok.context(IComment)
    grok.name('copy-attachment-to-answer')

    def render(self):
        context = aq_inner(self.context)
        conversation = aq_parent(context)
        answer = aq_parent(conversation)
        file = getattr(context, 'attachment', None)
        filename = answer.invokeFactory(
            id=file.filename,
            type_name='ESDRTFile',
            file=file,
        )
        return self.request.response.redirect(context.absolute_url())
