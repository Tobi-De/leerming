from .models import Profile


def register_users_to_reviews():
    """Make sure all users are registered to a review."""

    for profile in Profile.objects.all():
        profile.register_for_next_review()
