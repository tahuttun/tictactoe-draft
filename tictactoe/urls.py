# tictactoe/urls.py
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, GameViewSet, MoveViewSet, BestPlayersView, GameBoardView, DeleteGameView
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'moves', MoveViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('best-players/', BestPlayersView.as_view(), name='best-players'),
    path('games/<int:game_id>/board/', GameBoardView.as_view(), name='game-board'),
    path('games/<int:game_id>/delete/', DeleteGameView.as_view(), name='delete-game'),
]
