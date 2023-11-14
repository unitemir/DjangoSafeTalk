import base64
import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, ChatRoom, User
from .encryption_utils import encrypt_message, decrypt_message
from cryptography.fernet import Fernet


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_id}'

        if await self.is_room_exists(self.room_id):
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        else:
            await self.close()

    @database_sync_to_async
    def is_room_exists(self, room_id):
        return ChatRoom.objects.filter(id=room_id).exists()

    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        username = user.username if user.username else user

        # Получаем ключ шифрования из переменной окружения
        encryption_key = os.environ.get('ENCRYPTION_KEY')

        if encryption_key:
            encrypted_message = encrypt_message(message, encryption_key)

            await self.save_message(base64.b64encode(encrypted_message).decode(), user)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': base64.b64encode(encrypted_message).decode(),
                    'user': username,
                }
            )
        else:
            print("Encryption key not found.")

    async def chat_message(self, event):
        message = event['message']

        encrypted_message = base64.b64decode(message)
        key = await self.take_encryption_key()
        decrypted_message = decrypt_message(encrypted_message, key)
        username = event['user']
        await self.send(text_data=json.dumps({
            'message': decrypted_message,
            'user': username,
        }))

    @database_sync_to_async
    def save_message(self, encrypted_message, user):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            print(f"Chat room {self.room_id} does not exist.")
            return

        if user.is_authenticated:
            # Если пользователь аутентифицирован, сохраняем сообщение
            Message.objects.create(
                chat_room=room,
                user=user,
                text=encrypted_message
            )
        else:
            print("User is not authenticated.")

    @database_sync_to_async
    def take_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user
        except:
            return

    @database_sync_to_async
    def take_encryption_key(self):
        try:
            return os.environ.get('ENCRYPTION_KEY')
        except:
            pass
