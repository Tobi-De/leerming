from leerming.users.models import User

from django.core.mail import get_connection
from django.conf import settings

from typing import TypedDict

class EmailRecipient(TypedDict):
    email: str
    context: dict
    html_body: str
    
class WebPushRecipient(TypedDict):
    ...

class TelegramRecipient(TypedDict):
    phone_number: str
    context: dict
    message:str


def email_channel(recipients:list[EmailRecipient]):
    connection = get_connection()
    from_email = settings.DEFAULT_FROM_EMAIL
    # construct emails for each reviewer
    ...

def web_push_channel(recipients:list[WebPushRecipient]):
    # construct push notifications for each reviewer
    ...

def telegram_channel(recipients:list[TelegramRecipient]):
    # construct telegram messages for each reviewer
    ...


def notify_reviewers(reviewers:list[User]):
    # group reviewers by channels that are available to them
    # send notifications via each channel
    ...



