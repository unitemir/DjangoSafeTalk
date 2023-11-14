from django.urls import path

from . import views
from .views import MessageListView, home
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('messages/<int:chat_room_id>/', MessageListView.as_view(), name='message_list'),
    path('signup/', views.signup, name='signup'),
    path('home/', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('start-chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<str:room_name>/<str:other_user>/', views.chat_room, name='chat_room'),
]
