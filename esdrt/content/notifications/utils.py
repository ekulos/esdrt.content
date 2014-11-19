from cs.htmlmailer.mailer import create_html_mail
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from zope.globalrequest import getRequest


def notify(observation, template, subject, roles=[]):
    users = get_users_in_context(observation, roles=roles)
    content = template(**dict(observation=observation))
    send_mail(subject, safe_unicode(content), users)


def send_mail(subject, email_content, users=[]):
    """
    Effectively send the e-mail message
    """
    from_addr = api.portal.get().email_from_address
    user_emails = extract_emails(users)
    if user_emails:
        to_addr = user_emails[0]
        cc_addrs = user_emails[1:]
        request = getRequest()

        mail = create_html_mail(subject,
            html=email_content,
            from_addr=from_addr,
            to_addr=to_addr,
            cc_addrs=cc_addrs,
        )

        try:
            mailhost = api.portal.get_tool('MailHost')
            mailhost.send(mail.as_string())
            message = u'Users have been notified by e-mail'
            IStatusMessage(request).add(message)
        except:
            message = u'There was an error sending the notification, but your action was completed succesfuly. Contact the EEA Secretariat for further instructions.'
            IStatusMessage(request).add(message, type='error')


def extract_emails(users):
    """
    Get the email of each user
    """
    emails = []
    for user in users:
        email = user.getProperty('email')
        if email:
            emails.append(email)

    return list(set(emails))


def get_users_in_context(observation, roles):
    users = []
    local_roles = observation.get_local_roles()
    role_dict = {}
    role_dict['ReviewerPhase1'] = []
    role_dict['ReviewerPhase2'] = []
    role_dict['QualityExpert'] = []
    role_dict['LeadReviewer'] = []
    role_dict['MSAuthority'] = []
    role_dict['CounterPart'] = []
    role_dict['MSExpert'] = []
    for username, userroles in local_roles:
        for userrole in userroles:
            if userrole in role_dict.keys():
                role_dict[userrole].append(username)

    usernames = []
    for role in roles:
        usernames.extend(role_dict.get(role, []))

    for username in usernames:
        user = api.user.get(username=username)
        users.append(user)

    return users
