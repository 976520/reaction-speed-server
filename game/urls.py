from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('leaderboard/', views.get_leaderboard, name='leaderboard'),
] 