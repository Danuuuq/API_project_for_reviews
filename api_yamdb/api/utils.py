from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def send_code(data):
    """Функция отправки письма с кодом регистрации."""
    user = data.username
    email = data.email
    confirmation_code = data.confirmation_code
    subject = 'Welcome to YaMDb'
    message = (
        f'{user}, добро пожаловать на сайт YaMDb! Для получения '
        f'токена используйте код доступа: <{confirmation_code}>')
    from_email = settings.EMAIL_FROM
    try:
        send_mail(subject, message, from_email, [email])
    except BadHeaderError:
        return Response({'Error': 'Invalid header found.'},
                        status=status.HTTP_400_BAD_REQUEST)
    except SMTPException as error:
        return Response({'Error': error},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_tokens_for_user(user):
    """Функция для выдачи токена пользователю."""
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token),
    }
