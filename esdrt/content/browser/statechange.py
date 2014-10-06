from Acquisition import aq_inner
from Acquisition import aq_parent
from esdrt.content import MessageFactory as _
from plone import api
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form.form import Form
from zope import schema
from zope.interface import Interface


class IFinishObservationReasonForm(Interface):

    reason = schema.Choice(
        title=_(u'Finishing reason'),
        vocabulary='esdrt.content.finishobservationreasons',
        required=True,
    )

    comments = RichText(
        title=_(u'Enter comments if you want'),
        required=False,
    )


class FinishObservationReasonForm(Form):
    fields = field.Fields(IFinishObservationReasonForm)
    label = _(u'Finish observation')
    description = _(u'Check the reason for requesting the closure of this observation')
    ignoreContext = True

    @button.buttonAndHandler(u'Finish observation')
    def finish_observation(self, action):
        reason = self.request.get('form.widgets.reason')[0]
        comments = self.request.get('form.widgets.comments')
        with api.env.adopt_roles(['Manager']):
            self.context.closing_reason = reason
            self.context.closing_comments = RichTextValue(comments, 'text/html', 'text/html')
            if api.content.get_state(self.context) == 'phase1-conclusions':
                return self.context.content_status_modify(
                    workflow_action='phase1-request-close',
                )
            elif api.content.get_state(self.context) == 'phase2-conclusions':
                return self.context.content_status_modify(
                    workflow_action='phase2-finish-observation',
                )

        self.request.response.redirect(context.absolute_url())


    def updateActions(self):
        super(FinishObservationReasonForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')



class IDenyFinishObservationReasonForm(Interface):

    reason = schema.Choice(
        title=_(u'Denying reason'),
        vocabulary='esdrt.content.finishobservationdenyreasons',
        required=True,
    )

    comments = RichText(
        title=_(u'Enter comments if you want'),
        required=False,
    )


class DenyFinishObservationReasonForm(Form):
    fields = field.Fields(IDenyFinishObservationReasonForm)
    label = _(u'Deny finish observation')
    description = _(u'Check the reason for denying the finishing of this observation')
    ignoreContext = True

    @button.buttonAndHandler(u'Deny finishing observation')
    def finish_observation(self, action):
        reason = self.request.get('form.widgets.reason')[0]
        comments = self.request.get('form.widgets.comments')
        with api.env.adopt_roles(['Manager']):
            self.context.closing_deny_reason = reason
            self.context.closing_deny_comments = RichTextValue(comments, 'text/html', 'text/html')
            import pdb; pdb.set_trace()
            if api.content.get_state(self.context) == 'phase1-close-requested':
                return self.context.content_status_modify(
                    workflow_action='phase1-deny-closure',
                )
            elif api.content.get_state(self.context) == 'phase2-close-requested':
                return self.context.content_status_modify(
                    workflow_action='phase2-deny-finishing-observation',
                )

        return self.response.redirect(self.context.absolute_url())

    def updateActions(self):
        super(DenyFinishObservationReasonForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


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

    index = ViewPageTemplateFile('templates/assign_answerer_form.pt')

    def target_groupname(self):
        context = aq_inner(self.context)
        observation = aq_parent(context)
        country = observation.country.lower()
        return 'extranet-esd-countries-msexpert-%s' % country

    def get_counterpart_users(self):
        groupname = self.target_groupname()
        current = api.user.get_current()
        current_id = current.getId()
        return [u for u in api.user.get_users(groupname=groupname) if current_id != u.getId()]

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

            if isinstance(usernames, basestring):
                user = api.user.get(username=usernames)
                groupname = self.target_groupname()
                if groupname not in user.getGroups():
                    status = IStatusMessage(self.request)
                    msg = _(u'Selected user is not valid')
                    status.addStatusMessage(msg, "error")
                    return self.index()

                api.user.grant_roles(username=usernames,
                    roles=['MSExpert'],
                    obj=self.context)
                api.user.grant_roles(username=usernames,
                    roles=['MSExpert'],
                    obj=observation)
            else:
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

            wf_action = 'phase1-assign-answerer'
            return self.context.content_status_modify(
                workflow_action=wf_action,
            )

        else:
            return self.index()

    def updateActions(self):
        super(AssignAnswererForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class IAssignCounterPartForm(Interface):
    counterpart = schema.TextLine(
        title=_(u'Select the counterpart'),
    )

    workflow_action = schema.TextLine(
        title=_(u'Workflow action'),
        required=True
    )


class AssignCounterPartForm(BrowserView):

    index = ViewPageTemplateFile('templates/assign_counterpart_form.pt')

    def target_groupnames(self):
        return [
            'extranet-esd-ghginv-sr',
            'extranet-esd-ghginv-qualityexpert',
            'extranet-esd-esdreview-reviewexp',
            'extranet-esd-esdreview-leadreview',
        ]

    def assignation_target(self):
        return aq_parent(aq_inner(self.context))

    def get_counterpart_users(self):
        current = api.user.get_current()
        current_id = current.getId()

        users = []

        def isCP(u):
            target = self.assignation_target()
            return 'CounterPart' in api.user.get_roles(user=u, obj=target)

        for groupname in self.target_groupnames():
            data = [(u, isCP(u)) for u in api.user.get_users(groupname=groupname) if current_id != u.getId()]
            users.extend(data)

        return users

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        target = self.assignation_target()
        if self.request.form.get('send', None):
            counterparts = self.request.get('counterparts', None)
            #comments = self.request.get('comments', None)
            if counterparts is None:
                status = IStatusMessage(self.request)
                msg = _(u'You need to select at least one counterpart')
                status.addStatusMessage(msg, "error")
                return self.index()

            for user, cp in self.get_counterpart_users():
                if cp:
                    api.user.revoke_roles(user=user,
                        roles=['CounterPart'],
                        obj=target,
                    )

            if isinstance(counterparts, basestring):
                api.user.grant_roles(username=counterparts,
                    roles=['CounterPart'],
                    obj=target)
            else:
                for username in counterparts:
                    api.user.grant_roles(username=username,
                        roles=['CounterPart'],
                        obj=target)
            # if not comments:
            #     status = IStatusMessage(self.request)
            #     msg = _(u'You need to enter some comments for your counterpart')
            #     status.addStatusMessage(msg, "error")
            #     return self.index()
            wf_action = 'phase1-request-for-counterpart-comments'
            #wf_comments = self.request.get('comments')
            return self.context.content_status_modify(
                workflow_action=wf_action,

            )

        else:
            return self.index()

    def updateActions(self):
        super(AssignCounterPartForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')


class IAssignConclusionReviewerForm(Interface):
    reviewers = schema.Choice(
        title=_(u'Select the conclusion reviewers'),
        vocabulary=u'plone.app.vocabularies.Users',
    )


class AssignConclusionReviewerForm(BrowserView):

    index = ViewPageTemplateFile('templates/assign_conclusion_reviewer_form.pt')

    def target_groupnames(self):
        return [
            'extranet-esd-ghginv-sr',
            'extranet-esd-ghginv-qualityexpert',
            'extranet-esd-esdreview-reviewexp',
            'extranet-esd-esdreview-leadreview',
        ]

    def get_counterpart_users(self):
        current = api.user.get_current()
        current_id = current.getId()

        users = []

        def isCP(u):
            return 'CounterPart' in api.user.get_roles(user=u, obj=self.context)

        for groupname in self.target_groupnames():
            data = [(u, isCP(u)) for u in api.user.get_users(groupname=groupname) if current_id != u.getId()]
            users.extend(data)

        return users

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        if self.request.form.get('send', None):
            usernames = self.request.form.get('counterparts', None)
            if not usernames:
                status = IStatusMessage(self.request)
                msg = _(u'You need to select at least one reviewer for conclusions')
                status.addStatusMessage(msg, "error")
                return self.index()

            for user, cp in self.get_counterpart_users():
                if cp:
                    api.user.revoke_roles(user=user,
                        obj=self.context,
                        roles=['CounterPart']
                    )

            for username in usernames:
                api.user.grant_roles(username=username,
                    roles=['CounterPart'],
                    obj=self.context)

            wf_action = 'phase1-request-comments'
            return self.context.content_status_modify(
                workflow_action=wf_action,
            )

        else:
            return self.index()

    def updateActions(self):
        super(AssignConclusionReviewerForm, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass('standardButton')
