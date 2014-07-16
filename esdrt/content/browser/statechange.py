from Acquisition import aq_parent
from plone.app.textfield import RichText
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
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface


class IObservationClosingReasonForm(Interface):

    reason = schema.Choice(
        title=_(u'Closing reason'),
        vocabulary='esdrt.content.closingreasons',
        required=True,
    )

    comments = RichText(
        title=_(u'Enter comments if you want'),
        required=False,
    )


class ObservationClosingReasonForm(Form):
    fields = field.Fields(IObservationClosingReasonForm)
    label = _(u'Close observation')
    description = _(u'Check the reason for closing this observation')
    ignoreContext = True

    @button.buttonAndHandler(u'Close observation')
    def close_observation(self, action):
        reason = self.request.get('reason')
        comments = self.request.get('comments')
        with api.env.adopt_roles(['Manager']):
            self.context.closing_reason = reason
            self.context.closing_comments = comments
        return self.context.content_status_modify(
            workflow_action='close-observation',
        )


class IAssignAnswererForm(Interface):
    answerers = schema.Choice(
        title=_(u'Select the answerers'),
        vocabulary=u'plone.app.vocabularies.Users',
    )

    workflow_action = schema.TextLine(
        title=_(u'Workflow action'),
        required=True
    )


class AssignAnswererForm(BrowserView):

    index = ViewPageTemplateFile('assign_answerer_form.pt')

    def target_groupname(self):
        context = aq_inner(self.context)
        observation = aq_parent(context)
        country = observation.country.lower()
        return 'extranet-esd-ms-experts-%s' % country

    def get_counterpart_users(self):
        groupname = self.target_groupname()
        current = api.user.get_current()
        return [u for u in api.user.get_users(groupname=groupname) if current.getId() != u.getId()]

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        context = aq_inner(self.context)
        observation = aq_parent(context)
        if self.request.form.get('send', None):
            usernames = self.request.get('answerers', None)
            if not usernames:
                status = IStatusMessage(self.request)
                msg = _(u'You need to select at least one commenter for discussion')
                status.addStatusMessage(msg, "error")
                return self.index()

            for username in usernames:
                user = api.user.get(username=username)
                groupname = self.target_groupname()
                if groupname not in user.getGroups():
                    status = IStatusMessage(self.request)
                    msg = _(u'Selected user is not valid')
                    status.addStatusMessage(msg, "error")
                    return self.index()

            for username in usernames:
                api.user.grant_roles(username=username,
                    roles=['MSExpert'],
                    obj=self.context)
                api.user.grant_roles(username=username,
                    roles=['MSExpert'],
                    obj=observation)

            wf_action = 'assign-answerer'
            return self.context.content_status_modify(
                workflow_action=wf_action,
            )

        else:
            return self.index()


class IAssignCounterPartForm(Interface):
    counterpart = schema.TextLine(
        title=_(u'Select the counterpart'),
    )

    workflow_action = schema.TextLine(
        title=_(u'Workflow action'),
        required=True
    )


class AssignCounterPartForm(BrowserView):

    index = ViewPageTemplateFile('assign_counterpart_form.pt')
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
            #comments = self.request.get('comments', None)
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

            # if not comments:
            #     status = IStatusMessage(self.request)
            #     msg = _(u'You need to enter some comments for your counterpart')
            #     status.addStatusMessage(msg, "error")
            #     return self.index()

            api.user.grant_roles(username=username,
                roles=['CounterPart'],
                obj=self.context)
            wf_action = 'request-for-counterpart-comments'
            #wf_comments = self.request.get('comments')
            return self.context.content_status_modify(
                workflow_action=wf_action,

            )

        else:
            return self.index()


class IAssignConclusionReviewerForm(Interface):
    reviewers = schema.Choice(
        title=_(u'Select the conclusion reviewers'),
        vocabulary=u'plone.app.vocabularies.Users',
    )


class AssignConclusionReviewerForm(BrowserView):

    index = ViewPageTemplateFile('assign_conclusion_reviewer_form.pt')

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
            usernames = self.request.get('reviewers', None)
            if not usernames:
                status = IStatusMessage(self.request)
                msg = _(u'You need to select at least one reviewer for conclusions')
                status.addStatusMessage(msg, "error")
                return self.index()

            for username in usernames:
                user = api.user.get(username=username)
                groupname = self.target_groupname()
                if groupname not in user.getGroups():
                    status = IStatusMessage(self.request)
                    msg = _(u'Selected user is not valid')
                    status.addStatusMessage(msg, "error")
                    return self.index()

            for username in usernames:
                api.user.grant_roles(username=username,
                    roles=['ConclusionReviewer'],
                    obj=self.context)

            wf_action = 'request-comments'
            return self.context.content_status_modify(
                workflow_action=wf_action,
            )

        else:
            return self.index()