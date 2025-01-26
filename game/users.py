import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Game
import asyncio
import random

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game = None
        self.player_ip = self.scope['client'][0]
        await self.accept()
        
        game = await self.find_or_create_game()
        self.game_id = str(game.id)
        await self.channel_layer.group_add(self.game_id, self.channel_name)
        
        if game.player1_ip and game.player2_ip:
            await self.start_game()

    async def disconnect(self, close_code):
        if self.game_id:
            await self.channel_layer.group_discard(self.game_id, self.channel_name)
            await self.end_game()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'click':
            game = await self.get_game()
            if game.status == Game.PLAYING:
                await self.handle_click(data.get('timestamp'))

    @database_sync_to_async
    def find_or_create_game(self):
        game = Game.objects.filter(status=Game.WAITING).first()
        
        if game and game.player1_ip and not game.player2_ip:
            game.player2_ip = self.player_ip
            game.save()
            return game
            
        if not game:
            game = Game.objects.create(player1_ip=self.player_ip)
            
        return game

    async def start_game(self):
        await self.channel_layer.group_send(
            self.game_id,
            {
                'type': 'game_message',
                'message': {
                    'action': 'start',
                    'delay': random.randint(2000, 7000)
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
    def set_winner(self, winner_ip):
        game = Game.objects.get(id=self.game_id)
        game.winner_ip = winner_ip
        game.status = Game.FINISHED
        game.finished_at = timezone.now()
        game.save() 