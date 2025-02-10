from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('leaderboard/', views.get_leaderboard, name='leaderboard'),
    path('validate-token/', views.validate_token, name='validate-token'),
] 