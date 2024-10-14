from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.db import models


class UserManagerApi(UserManager):

    def create_user(self, username, email, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return super().create_user(username, email, **extra_fields)


class User(AbstractUser):
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль', max_length=settings.MAX_LENGTH_ROLE,
        choices=settings.ROLE_USERS,
        default=settings.ROLE_USERS[0][0], auto_created=True)
    email = models.CharField(
        'email', max_length=settings.MAX_LENGTH_EMAIL, unique=True)
    confirmation_code = models.CharField(
        'Код подтверждения', max_length=settings.MAX_LENGTH_CONFIRMATION_CODE,
        blank=True)

    objects = UserManager()

    @property
    def is_admin(self):
        return self.role == settings.ROLE_USERS[2][0]

    @property
    def is_moderate(self):
        return self.role == settings.ROLE_USERS[1][0]

    class Meta:
        ordering = ('username', 'id')
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
