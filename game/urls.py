from django.urls import path
from . import views

urlpatterns = [
    path('character/new/', views.CharacterCreateView.as_view(), name='game-character-create'),
    path('user/<str:username>/', views.user_view, name='game-user-detail'),
    path('users/', views.AllUsersView.as_view(), name='game-users-all'),
    path('news/', views.PostListView.as_view(), name='game-news'),
    path('play/', views.game_view, name='game-view'),

    # channels

    path('chat/', views.chat, name='game-chat'),
    path('chat/<str:room_name>/', views.room_view, name='game-chat-room'),

    # test

    path('test_game/', views.test_game, name='test-game')
]
