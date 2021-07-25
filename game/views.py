import json
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib.auth.models import User
from .models import Post, Character
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import os


def test_game(request):
    if request.user.is_authenticated:
        user = request.user
        f = os.path.join(settings.BASE_DIR, 'game/static/game/assets/characters.json')

        with open(f) as json_file:
            data = json.load(json_file)

        context = {
            'user': user.username,
            'id': user.pk,
            'characters': Character.objects.filter(owner=user.pk),
            'skins': data['characters']
        }
        return render(request, 'game/test_game.html', context)
    else:
        return redirect(settings.LOGIN_URL)


def user_view(request, username):
    if request.user.is_authenticated:
        u = User.objects.filter(username=username).first()
        if u is not None:
            u_id = u.pk
            context = {
                'user': u,
                'id': u_id,
                'posts': Post.objects.filter(author=u_id),
                'characters': Character.objects.filter(owner=u_id)
            }
            return render(request, 'game/user_page.html', context)
        else:
            messages.warning(request, 'searched user does not exist.')
            return redirect('game-users-all')
    else:
        return redirect(settings.LOGIN_URL)


def news_view(request):
    if request.user.is_authenticated:
        context = {
            'posts': Post.objects.all(),
        }
        return render(request, 'game/news.html', context)
    else:
        return redirect(settings.LOGIN_URL)


def all_users_view(request):
    if request.user.is_authenticated:
        context = {
            'users': User.objects.all()
        }
        return render(request, 'game/users_all.html', context)
    else:
        return redirect(settings.LOGIN_URL)


# not used :(


class PostListView(ListView):
    model = Post
    template_name = 'game/news.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10


class AllUsersView(ListView):
    context_object_name = 'users'
    queryset = User.objects.all()
    template_name = 'game/users_all.html'


class CharacterCreateView(LoginRequiredMixin, CreateView):
    template_name = 'game/character_create.html'
    model = Character
    fields = ['name', 'texture', 'strength', 'agility', 'attack', 'defense', 'vitality', 'charisma', 'stamina', 'magick']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
