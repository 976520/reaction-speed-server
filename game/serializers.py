from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import PlayerProfile

User = get_user_model()

class PlayerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ('wins', 'losses', 'total_games', 'best_reaction_time')

class UserSerializer(serializers.ModelSerializer):
    profile = PlayerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'profile')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {
                'error_messages': {
                    'unique': '이미 존재하는 사용자 이름입니다.'
                }
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        PlayerProfile.objects.create(user=user)
        return user 