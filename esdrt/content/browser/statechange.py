from Acquisition import aq_inner
from esdrt.content import MessageFactory as _
from esdrt.content.question import IQuestion
from five import grok
from plone import api
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
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


class AssignCounterPartForm(BrowserView):

    index = ViewPageTemplateFile('assing_counterpart_form.pt')
    # macro_wrapper = ViewPageTemplateFile('macro_wrapper.pt')

    def target_groupname(self):
        context = aq_inner(self.context)
        country = context.country.lower()
        sector = context.ghg_source_sectors
        return 'extranet-esd-reviewexperts-%s-%s' % (sector, country)

    def get_counterpart_users(self):
        groupname = self.target_groupname()
        current = api.user.get_current()
        return [u for u in api.user.get_users(groupname=groupname) if current.getId() != u.getId()]

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        if self.request.form.get('send', None):
            username = self.request.get('counterpart', None)
            comments = self.request.get('comments', None)
            if username is None:
                status = IStatusMessage(self.request)
                msg = _(u'You need to select one counterpart')
                status.addStatusMessage(msg, "error")
                return self.index()

            user = api.user.get(username=username)
            groupname = self.target_groupname()
            if groupname not in user.getGroups():
                status = IStatusMessage(self.request)
                msg = _(u'Selected user is not valid')
                status.addStatusMessage(msg, "error")
                return self.index()

            if not comments:
                status = IStatusMessage(self.request)
                msg = _(u'You need to enter some comments for your counterpart')
                status.addStatusMessage(msg, "error")
                return self.index()

            api.user.grant_roles(username=username,
                roles=['CounterPart'],
                obj=self.context)
            wf_action = 'request-for-counterpart-comments'
            wf_comments = self.request.get('comments')
            return self.context.content_status_modify(
                workflow_action=wf_action,
                comment=wf_comments
            )

        else:
            return self.index()


class ISendCounterPartComments(Interface):
    comments = schema.Text(
        title=_(u'Enter the comments'),
        required=True
    )


class SendCounterPartComments(form.Form):
    grok.context(IQuestion)
    grok.name('send_counterpart_comments')
    grok.require('cmf.ModifyPortalContent')

    fields = field.Fields(ISendCounterPartComments)
    label = _(u'Send comments')
    ignoreContext = True

    @button.buttonAndHandler(u'Send comments')
    def send_comments(self, action):
        wf_action = 'send-comments'
        wf_comments = self.request.get('form.widgets.comments')
        return self.context.content_status_modify(
            workflow_action=wf_action,
            comment=wf_comments
        )