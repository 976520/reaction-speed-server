from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'total_games', 'wins', 'best_reaction_time')
        read_only_fields = ('id', 'total_games', 'wins', 'best_reaction_time')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        
        user = User.objects.create_user(
            username=username,
            password=password
        )
        return user 