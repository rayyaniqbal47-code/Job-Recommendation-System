from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


def send_application_accept_or_reject_email(request , application , mail_subject , email_template):
    
    from_email = settings.DEFAULT_FROM_EMAIL

    current_site = get_current_site(request)

    message = render_to_string(email_template , {
        "user":application.jobseeker.customuser.username,
        'domain':current_site,
        "job":application.job,

    })
    to_email = application.jobseeker.customuser.email
    mail = EmailMessage(subject=mail_subject , body=message , from_email=from_email , to=[to_email])
    mail.content_subtype = "html"
    mail.send()












