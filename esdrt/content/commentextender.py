"""
    Documentation:
        -   https://github.com/tisto/collective.ploneboard/blob/master/src/collective/ploneboard/browser/commentextender.py
        -   http://plone.293351.n2.nabble.com/GSoC-2014-Collective-Ploneboard-Attachment-issue-tp7571746p7571837.html
"""
from esdrt.content import MessageFactory as _
from persistent import Persistent
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Acquisition import Implicit
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.comment import Comment
from plone.namedfile.field import NamedBlobFile
from plone.z3cform.fieldsets import extensible
from Products.CMFCore import permissions
from z3c.form.field import Fields
from zope import interface
from zope.annotation import factory
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICommentExtenderFields(Interface):
    attachment = NamedBlobFile(
        title=_(u"Attachment"),
        description=_(u""),
        required=False,
    )


class CommentExtenderFields(Implicit, Persistent):
    interface.implements(ICommentExtenderFields)
    adapts(Comment)
    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'attachment')
    attachment = u""

InitializeClass(CommentExtenderFields)

CommentExtenderFactory = factory(CommentExtenderFields)


class CommentExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, CommentForm)

    fields = Fields(ICommentExtenderFields)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        self.add(ICommentExtenderFields, prefix="")
        self.move('attachment', after='text', prefix="")
