from rest_framework import serializers
from .models import ChatRoom, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'name']


class MessageSerializer(serializers.ModelSerializer):
    decrypted_text = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'user', 'decrypted_text', 'timestamp']

