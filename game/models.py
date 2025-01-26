from django.db import models

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