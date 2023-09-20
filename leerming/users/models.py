from improved_user.model_mixins import AbstractUser


class User(AbstractUser):
    def __str__(self):
        return self.short_name or self.full_name or self.email
