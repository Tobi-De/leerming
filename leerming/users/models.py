from typing import TYPE_CHECKING

from improved_user.model_mixins import AbstractUser

if TYPE_CHECKING:
    from leerming.profiles.models import Profile


class User(AbstractUser):
    profile: Profile

    def __str__(self):
        return self.short_name or self.full_name or self.email
