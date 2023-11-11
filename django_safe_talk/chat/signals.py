import os

from cryptography.fernet import Fernet
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    encryption_key = Fernet.generate_key().decode()
    os.environ['ENCRYPTION_KEY'] = encryption_key


@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    if 'ENCRYPTION_KEY' in os.environ:
        del os.environ['ENCRYPTION_KEY']
