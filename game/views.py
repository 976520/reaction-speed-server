from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    print(request.data) 
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        print(serializer.errors)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    return Response({
        'user': UserSerializer(user).data,
        'message': '회원가입이 완료되었습니다.',
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard(request):
    users = User.objects.filter(total_games__gt=0).order_by('-wins', 'best_reaction_time')[:10]
    return Response(UserSerializer(users, many=True).data) 