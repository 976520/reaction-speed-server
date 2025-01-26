import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Game
import random
from django.db.models import Q

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_ip = self.scope['client'][0]
        await self.accept()
        
        game = await self.find_or_create_game()
        self.game_id = str(game.id)
        await self.channel_layer.group_add(self.game_id, self.channel_name)
        
        if game.player1_ip and game.player2_ip:
            await self.start_game()

    async def disconnect(self, close_code):
        if hasattr(self, 'game_id'):
            await self.channel_layer.group_discard(self.game_id, self.channel_name)
            await self.end_game()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'search_game':
            game = await self.find_or_create_game()
            if game.player1_ip and game.player2_ip:
                await self.channel_layer.group_send(
                    self.game_id,
                    {
                        'type': 'game_message',
                        'message': {
                            'action': 'start',
                            'gameId': str(game.id),
                            'opponentIp': self.player_ip
                        }
                    }
                )
        elif action == 'click':
            await self.handle_click(data.get('timestamp'))

    @database_sync_to_async
    def find_or_create_game(self):
        game = Game.objects.filter(status=Game.WAITING, player2_ip__isnull=True).first()
        
        if game:
            if game.player1_ip != self.player_ip:
                game.player2_ip = self.player_ip
                game.save()
                return game
            return None  
        
        existing_game = Game.objects.filter(
            Q(player1_ip=self.player_ip) | Q(player2_ip=self.player_ip),
            status__in=[Game.WAITING, Game.PLAYING]
        ).first()
        
        if not existing_game:
            return Game.objects.create(player1_ip=self.player_ip)
        
        return None

    async def start_game(self):
        game = await self.get_game()
        game.status = Game.PLAYING
        game.started_at = timezone.now()
        await self.save_game(game)
        
        await self.channel_layer.group_send(
            self.game_id,
            {
                'type': 'game_message',
                'message': {
                    'action': 'start',
                    'gameId': self.game_id,
                    'opponentIp': self.player_ip
                }
            }
        )

    async def handle_click(self, timestamp):
        game = await self.get_game()
        if game.status == Game.PLAYING:
            await self.set_winner(self.player_ip)
            await self.channel_layer.group_send(
                self.game_id,
                {
                    'type': 'game_message',
                    'message': {
                        'action': 'game_over',
                        'winner': self.player_ip,
                        'timestamp': timestamp
                    }
                }
            )

    async def game_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_game(self):
        return Game.objects.get(id=self.game_id)

    @database_sync_to_async
    def save_game(self, game):
        game.save()

    @database_sync_to_async
    def set_winner(self, winner_ip):
        game = Game.objects.get(id=self.game_id)
        game.winner_ip = winner_ip
        game.status = Game.FINISHED
        game.finished_at = timezone.now()
        game.save()

    async def end_game(self):
        game = await self.get_game()
        if game.status != Game.FINISHED:
            game.status = Game.FINISHED
            game.finished_at = timezone.now()
            await self.save_game(game) 