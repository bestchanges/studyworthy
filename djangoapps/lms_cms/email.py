import logging

from cms.utils import get_current_site
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from djangoapps.lms.models import FlowLesson, Participant, ParticipantLesson
from djangoapps.utils import build_full_url

logger = logging.getLogger(__name__)


def send_notification_lesson_open(flow_lesson: FlowLesson):
    to_notify_query = ParticipantLesson.objects.filter(flow_lesson=flow_lesson,
                                                      participant__role=Participant.ROLE_STUDENT)
    for participant_lesson in to_notify_query:
        participant = participant_lesson.participant
        if not participant.user.email:
            logging.warning(f'No email for {participant}. Cannot sent new lesson notification.')
            continue
        lesson = flow_lesson.lesson
        context = {
            'participant_lesson': participant_lesson,
            'participant': participant,
            'flow_lesson': flow_lesson,
            'site': get_current_site(),
        }
        message = render_to_string('lms_cms/email/lesson_open_notification.txt', context)
        _send_mail(
            subject=_('New lesson available'),
            recipient_list=[participant.user.email],
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=True,
            message=message,
        )


def send_registration_email(user: User, password):
    site: Site = Site.objects.get_current()
    login_url = build_full_url(site=site, path=reverse('login'))
    context = {
        'user': user,
        'password': password,
        'site': site,
        'site_login_url': login_url,
    }
    message = render_to_string('lms_cms/email/user_creation_notification.txt', context)
    _send_mail(
        subject=_('Your account created'),
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=True,
        message=message,
    )


def send_notification_enrolled_to_flow(participant: Participant):
    site: Site = get_current_site()
    course = participant.flow.course
    user = participant.user
    context = {
        'user': user,
        'participant': participant,
        'site': site,
        'course': course,
    }
    message = render_to_string('lms_cms/email/user_notification_enrolled_to_flow.txt', context)
    _send_mail(
        subject=_('You enrolled to course'),
        recipient_list=[user.email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        fail_silently=True,
        message=message,
    )


def _send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None):
    logger.info(f'SENDING MAIL to {recipient_list} with subject {subject}')
    for rcpt in recipient_list:
        if rcpt:
            break
    else:
        raise ValueError(f'Empty recipient_list list for message: {subject}')
    send_mail(
        subject, message, from_email, recipient_list,
        fail_silently, auth_user, auth_password,
        connection, html_message
    )
