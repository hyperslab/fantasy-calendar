from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    db_table = 'auth_user'

    def __str__(self):
        return self.username
