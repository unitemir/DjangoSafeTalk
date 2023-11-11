import base64

from channels.db import database_sync_to_async
from django.core.cache import cache
from cryptography.fernet import Fernet, InvalidToken

# Функция для генерации ключа шифрования
def generate_key():
    return Fernet.generate_key()


# Функция для шифрования сообщения
def encrypt_message(message, key):
    if isinstance(key, str):
        key = key.encode()
    fernet = Fernet(key)
    if isinstance(message, str):
        message = message.encode()
    encrypted_message = fernet.encrypt(message)
    return encrypted_message


# Функция для дешифрования сообщения
def decrypt_message(message, key):
    try:
        if isinstance(key, str):
            key = key.encode()
        if isinstance(message, str):
            message = message.encode()
        fernet = Fernet(key)
        decrypted_message = fernet.decrypt(message)
        return decrypted_message.decode()
    except InvalidToken:
        return None
