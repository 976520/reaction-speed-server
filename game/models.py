from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=50, unique=True, null=True)
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
    player1_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_as_player1')
    player2_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_as_player2')
    winner_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='games_won') 