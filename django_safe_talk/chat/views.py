import base64
import os
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.generics import ListAPIView

from .encryption_utils import decrypt_message
from .models import Message, ChatRoom
from .serializers import MessageSerializer
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User


def start_chat(request, user_id):
    other_user = User.objects.get(id=user_id)
    existing_chat = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user).first()
    if existing_chat:
        return redirect('chat_room', room_name=existing_chat.name, other_user=other_user)
    else:
        ch_room, created = ChatRoom.objects.get_or_create(name=f"chat_{request.user.id}_{other_user.id}")
        ch_room.participants.add(request.user, other_user)
        return redirect('chat_room', room_name=ch_room.name, other_user=other_user)


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def home(request):
    users = User.objects.exclude(username=request.user.username)
    chat_rooms = ChatRoom.objects.all()
    return render(request, 'home.html', {'users': users, 'chat_rooms': chat_rooms})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def chat_room(request, room_name, other_user):
    if not request.user.is_authenticated:
        return redirect('login')
    ch_room = ChatRoom.objects.get(name=room_name)
    messages = Message.objects.filter(chat_room=ch_room).order_by('timestamp')
    key = os.environ.get('ENCRYPTION_KEY')
    decrypted_messages = []
    for message in messages:
        decrypted_text = decrypt_message(base64.b64decode(message.text), key)
        if decrypted_text is not None:
            message.text = decrypted_text
            decrypted_messages.append(message)
    return render(request, 'chat_room.html', {'roomUuid': ch_room.id, 'messages': decrypted_messages, 'other_user': other_user})


class MessageListView(ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_room_id = self.kwargs['chat_room_id']
        return Message.objects.filter(chat_room_id=chat_room_id)
