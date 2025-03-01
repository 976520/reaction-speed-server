import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Game
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
        
        existing_game = Game.objects.filter(
            Q(player1_ip=self.player_ip) | Q(player2_ip=self.player_ip),
            status__in=[Game.WAITING, Game.PLAYING]
        ).first()
        
        if existing_game:
            return existing_game
        
        return Game.objects.create(player1_ip=self.player_ip)

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
            await self.set_winner(self.player_ip, timestamp)
            
            if hasattr(self.scope, 'user') and self.scope.user.is_authenticated:
                await self.update_user_stats(self.scope.user, timestamp)

    async def game_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_game(self):
        return Game.objects.get(id=self.game_id)

    @database_sync_to_async
    def save_game(self, game):
        game.save()

    @database_sync_to_async
    def set_winner(self, winner_ip, reaction_time):
        game = Game.objects.get(id=self.game_id)
        game.winner_ip = winner_ip
        game.status = Game.FINISHED
        game.finished_at = timezone.now()
        game.save()
        
        if hasattr(self.scope, 'user') and self.scope.user.is_authenticated:
            self.update_user_stats(self.scope.user, reaction_time)

    @database_sync_to_async
    def update_user_stats(self, user, reaction_time):
        user.total_games += 1
        user.wins += 1
        if not user.best_reaction_time or reaction_time < user.best_reaction_time:
            user.best_reaction_time = reaction_time
        user.save()

    async def end_game(self):
        game = await self.get_game()
        if game.status != Game.FINISHED:
            game.status = Game.FINISHED
            game.finished_at = timezone.now()
            await self.save_game(game) 