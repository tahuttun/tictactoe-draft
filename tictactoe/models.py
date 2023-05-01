# models.py
from django.db import models
from itertools import product
import random

class Player(models.Model):
    username = models.CharField(max_length=255, unique=True)
    realname = models.CharField(max_length=255)
    total_games_played = models.IntegerField(default=0)
    total_games_won = models.IntegerField(default=0)
    total_games_lost = models.IntegerField(default=0)

    @property
    def win_loss_ratio(self):
        if self.total_games_lost == 0:
            return self.total_games_won
        return self.total_games_won / self.total_games_lost

class Game(models.Model):
    tic_user = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='tic_games')
    tac_user = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='tac_games')
    is_tic_turn = models.PositiveIntegerField(default=1)


    game_time = models.FloatField(null=True, blank=True)
    GAME_OUTCOMES = (
        ('win', 'Win'),
        ('lose', 'Lose'),
        ('draw', 'Draw'),
        ('going', 'On-Going')
    )
    game_outcome = models.CharField(max_length=10, choices=GAME_OUTCOMES)
    timestamp = models.DateTimeField(auto_now_add=True)

    grid_size = models.PositiveIntegerField(default=3)
    game_variation = models.CharField(max_length=255, null=True, blank=True)

    def get_total_moves(self):
        moves = self.move_set.all()
        return len(moves)

    def get_board(self, step=None):
        board = [['-' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        moves = self.move_set.all()
        if step is not None:
             moves = moves[:step]
        for move in moves:
           try:
               x, y = map(int, move.move.split(','))
               board[x][y] = move.piece
           except ValueError:
               continue

        return board


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    move_number = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    move = models.CharField(max_length=10)  # Example: "1,1"
    piece = models.CharField(max_length=1,default="X")  # X / O
    #player_name = models.CharField(max_length=255)  # Example: "player" or "AI"
    #player_name = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='moves')
    class Meta:
        ordering = ['timestamp']
    def validate_move(self):
        x, y = map(int, self.move.split(','))
        if x < 0 or x >= self.game.grid_size or y < 0 or y >= self.game.grid_size:
            raise ValidationError("Move is outside the grid")

        board = self.game.get_board()
        if board[x][y] != '-':
            raise ValidationError("Cell is already occupied")


    def save(self, *args, **kwargs):
        self.validate_move()
        super(Move, self).save(*args, **kwargs)
