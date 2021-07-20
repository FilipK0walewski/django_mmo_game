from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} Profile'


class Post(models.Model):
    objects = None
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Character(models.Model):
    objects = None
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    skin_color = models.TextField(default='white')
    texture = models.TextField(default='random')

    strength = models.IntegerField(default=1)
    agility = models.IntegerField(default=1)
    attack = models.IntegerField(default=1)
    defense = models.IntegerField(default=1)
    vitality = models.IntegerField(default=1)
    charisma = models.IntegerField(default=1)
    stamina = models.IntegerField(default=1)
    magick = models.IntegerField(default=1)

    gold = 0
    level = 1

    def __str__(self):
        return f'{self.owner.username}\'s character named {self.name}.'

    def get_info(self):
        info = {
            'stats': {
                'strength': self.strength,
                'agility': self.agility,
                'attack': self.attack,
                'defense': self.defense,
                'vitality': self.vitality,
                'charisma': self.charisma,
                'stamina': self.stamina,
                'magick': self.magick,
                'level': self.level,
                'gold': self.gold,
            },
            'skin': self.texture
        }
        return info
