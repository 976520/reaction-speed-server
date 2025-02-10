from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class User(AbstractUser):
    total_games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    best_reaction_time = models.IntegerField(null=True)

class Game(models.Model):
    WAITING = 'waiting'
    PLAYING = 'playing'
    FINISHED = 'finished'
    
    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (PLAYING, 'Playing'),
        (FINISHED, 'Finished'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WAITING)
    player1_ip = models.GenericIPAddressField(null=True)
    player2_ip = models.GenericIPAddressField(null=True)
    winner_ip = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    player1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_as_player2')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_won')

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    total_games = models.IntegerField(default=0)
    best_reaction_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username 