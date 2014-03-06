from esdrt.content import MessageFactory as _
from plone.app.workflow.browser.sharing import SharingView
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import Interface


class IAssignCounterPartForm(Interface):
    counterpart = schema.TextLine(
        title=_(u'Select the counterpart'),
    )

    comments = schema.Text(
        title=_(u'Enter the comments for your Counterpart'),
        required=True
    )

    workflow_action = schema.TextLine(
        title=_(u'Workflow action'),
        required=True
    )


class AssignCounterPartForm(SharingView):

    index = ViewPageTemplateFile('assing_counterpart_form.pt')
    macro_wrapper = ViewPageTemplateFile('macro_wrapper.pt')

    STICKY = []

    @memoize
    def roles(self):
        return [{'id': 'CounterPart', 'title': 'CounterPart'}]

    def group_search_results(self):
        return []

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        if self.request.get('form.button.Assign', None):
            wf_action = 'request-review'
            wf_comments = self.request.get('comments')
            return self.context.content_status_modify(
                workflow_action=wf_action,
                comment=wf_comments
            )

        else:
            postback = self.handle_form()
            if postback:
                return self.index()
            else:
                context_state = self.context.restrictedTraverse(
                    "@@plone_context_state")
                url = context_state.view_url()
                self.request.response.redirect(url)
