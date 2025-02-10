from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate, login
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
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'user': UserSerializer(user).data,
        'token': token.key,
        'message': '회원가입이 완료되었습니다.',
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(f"{username} 로그인")
    
    if not username or not password:
        return Response({
            'message': '아이디와 비밀번호를 모두 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        print(f"{username} 토큰: {token.key}")
        serializer = UserSerializer(user)
        response_data = {
            'user': serializer.data,
            'token': token.key,
            'message': '로그인이 완료되었습니다.'
        }
        print(f"{username} 응답: {response_data}")
        return Response(response_data)
    else:
        print(f"{username} 인증 실패")
        return Response({
            'message': '아이디 또는 비밀번호가 올바르지 않습니다.'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_leaderboard(request):
    users = User.objects.filter(total_games__gt=0).order_by('-wins', 'best_reaction_time')[:10]
    return Response(UserSerializer(users, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }) 