from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.template.loader import render_to_string
from html2text import html2text

from leerming.users.models import User


def email_channel(recipients: list[User], template_name: str, subject: str):
    connection = get_connection()
    from_email = settings.DEFAULT_FROM_EMAIL
    # construct emails for each reviewer
    messages = []
    for user in recipients:
        rendered_html_body = render_to_string(
            template_name, {"name": user.profile.short_name or user.profile.full_name}
        )
        message = EmailMultiAlternatives(
            subject,
            body=html2text(rendered_html_body),
            from_email=from_email,
            to=[user.email],
        )
        message.attach_alternative(rendered_html_body, "text/html")
        messages.append(message)

    connection.send_messages(messages)


def notify_reviewers(reviewers: list[User]):
    # group reviewers by channels that are available to them
    # send notifications via each channel
    email_users = [
        reviewer
        for reviewer in reviewers
        if reviewer.profile.email_notifications_enabled
    ]
    email_channel(
        email_users,
        template_name="emails/review_notification.html",
        subject="Notifications de Leerming",
    )
