from django.utils import timezone

from leerming.reviews.models import Review
from leerming.users.models import User


def send_review_notification(user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    last_review_was_today = (
        Review.get_last_review_date(reviewer=user) == timezone.now().date()
    )
    on_going_review = bool(Review.get_current_review(reviewer=user))
    if not last_review_was_today and not on_going_review:
        # TODO: send notification
        ...
