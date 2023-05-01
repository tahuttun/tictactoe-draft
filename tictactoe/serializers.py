# serializers.py
from rest_framework import serializers
from .models import Player, Game, Move

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    tic_user = PlayerSerializer()
    tac_user = PlayerSerializer()

    class Meta:
        model = Game
        fields = '__all__'

class MoveSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    #playername = serializers.CharField()
    move = serializers.CharField()
    class Meta:
        model = Move
        fields = ('game', 'move', 'timestamp')
