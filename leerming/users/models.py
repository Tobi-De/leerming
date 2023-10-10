from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from improved_user.managers import UserManager
from improved_user.model_mixins import DjangoIntegrationMixin
from improved_user.model_mixins import EmailAuthMixin

if TYPE_CHECKING:
    from leerming.profiles.models import Profile


class User(DjangoIntegrationMixin, EmailAuthMixin, PermissionsMixin, AbstractBaseUser):
    profile: "Profile"

    objects = UserManager()

    def __str__(self):
        return self.email
