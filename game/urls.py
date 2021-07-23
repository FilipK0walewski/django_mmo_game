from django.urls import path
from . import views

urlpatterns = [
    # path('character/new/', views.CharacterCreateView.as_view(), name='game-character-create'),
    path('user/<str:username>/', views.user_view, name='game-user-detail'),
    path('users/', views.all_users_view, name='game-users-all'),
    path('news/', views.news_view, name='game-news'),

    # test
    path('test_game/', views.test_game, name='test-game')
]