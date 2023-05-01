import math
from random import choice
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game, Move, Player
from .serializers import GameSerializer, MoveSerializer, PlayerSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def create(self, request, *args, **kwargs):
         if request.method != 'POST':
             return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

         tic_username = request.data.get('tic_user')
         tac_username = request.data.get('tac_user')
         tic_realname = request.data.get('tic_realname',tic_username)
         tac_realname = request.data.get('tac_realname',tac_username)
         grid_size = request.data.get('grid_size', 3)

         if not tic_username or not tac_username:
             return Response({"error": "Both tic_user and tac_user are required."},
                             status=status.HTTP_400_BAD_REQUEST)

         tic_user, _ = Player.objects.get_or_create(username=tic_username,realname=tic_realname)
         tac_user, _ = Player.objects.get_or_create(username=tac_username,realname=tac_realname)

         game = Game.objects.create(tic_user=tic_user, tac_user=tac_user, grid_size=grid_size)
         serializer = self.get_serializer(game)

         headers = self.get_success_headers(serializer.data)
         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class DeleteGameView(APIView):
     def delete(self, request, game_id, format=None):
         try:
             game = Game.objects.get(id=game_id)
             game.delete()
             return JsonResponse({"message": f"Game with ID {game_id} has been deleted."}, status=status.HTTP_200_OK)
         except Game.DoesNotExist:
             return JsonResponse({"error": f"Game with ID {game_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

def is_full(board, grid_size):
    for row in board:
        for cell in row:
            if cell == '-':
                return False
    return True

def get_winner(board, grid_size):
    directionX = [1, 0, 1, -1]
    directionY = [0, 1, 1, 1]
    win_length = 4 if grid_size >= 4 else grid_size

    def is_valid(x, y):
        return 0 <= x < grid_size and 0 <= y < grid_size

    for y in range(grid_size):
        for x in range(grid_size):
            player = board[x][y]
            if player in ['X', 'O']:
                for dx, dy in zip(directionX, directionY):
                    if all(
                        is_valid(x + dx * l, y + dy * l)
                        and board[x + dx * l][y + dy * l] == player
                        for l in range(win_length)
                    ):
                        return player
    return None

def count_potential_wins(board, grid_size, player):
    directionX = [1, 0, 1, -1]
    directionY = [0, 1, 1, 1]
    win_length = 4 if grid_size >= 4 else grid_size

    def is_valid(x, y, grid_size):
        return 0 <= x < grid_size and 0 <= y < grid_size

    score = 0

    for x in range(grid_size-win_length+1):
        for y in range(grid_size-win_length+1):
            if board[x][y] == player:
                for direction in range(len(directionX)):
                    empty_cell = 0
                    winning_candidate_len = 0

                    for l in range(win_length):
                        new_x = x + directionX[direction] * l
                        new_y = y + directionY[direction] * l

                        if not is_valid(new_x, new_y, grid_size):
                            break

                        cell = board[new_x][new_y]

                        if cell != player and cell != '-':
                            break
                        if cell == '-' and empty_cell:
                            break
                        if cell == '-' and not empty_cell:
                            empty_cell = 1

                        winning_candidate_len += 1

                    if win_length <= winning_candidate_len:
                        score += 1

    return score

def heuristic(board, grid_size):
     player_wins = count_potential_wins(board, grid_size, 'X')
     ai_wins = count_potential_wins(board, grid_size, 'O')

     return ai_wins - player_wins


def get_neighbors(board, grid_size, x, y, distance=2):
     neighbors = []
     for i in range(-distance, distance + 1):
         for j in range(-distance, distance + 1):
             if 0 <= x + i < grid_size and 0 <= y + j < grid_size:
                 neighbors.append((x + i, y + j))
     return neighbors

def get_relevant_moves(board, grid_size, distance=2):
     relevant_moves = set()
     for x in range(grid_size):
         for y in range(grid_size):
             if board[x][y] != '-':
                 neighbors = get_neighbors(board, grid_size, x, y, distance)
                 for neighbor in neighbors:
                     if board[neighbor[0]][neighbor[1]] == '-':
                         relevant_moves.add(neighbor)
     return list(relevant_moves)

def minimax(board, grid_size, depth, is_maximizing_player, alpha, beta, depth_limit):
     winner = get_winner(board, grid_size)
     if winner == 'X':
         return -1
     elif winner == 'O':
         return 1
     elif is_full(board, grid_size) or depth == depth_limit:
         return heuristic(board, grid_size)

     relevant_moves = get_relevant_moves(board, grid_size)

     if is_maximizing_player:
         best_value = -math.inf
         for move in relevant_moves:
             i, j = move
             if board[i][j] == '-':
                 board[i][j] = 'O'
                 value = minimax(board, grid_size, depth + 1, False, alpha, beta, depth_limit)
                 board[i][j] = '-'
                 best_value = max(best_value, value)
                 alpha = max(alpha, best_value)
                 if beta <= alpha:
                     break
         return best_value
     else:
         best_value = math.inf
         for move in relevant_moves:
             i, j = move
             if board[i][j] == '-':
                 board[i][j] = 'X'
                 value = minimax(board, grid_size, depth + 1, True, alpha, beta, depth_limit)
                 board[i][j] = '-'
                 best_value = min(best_value, value)
                 beta = min(beta, best_value)
                 if beta <= alpha:
                     break
         return best_value

def find_best_move(board, grid_size, depth_limit=4):
     best_value = -math.inf
     best_move = None
     relevant_moves = get_relevant_moves(board, grid_size)
     for move in relevant_moves:
         i, j = move
         if board[i][j] == '-':
             board[i][j] = 'O'
             move_value = minimax(board, grid_size, 0, False, -math.inf, math.inf, depth_limit)
             board[i][j] = '-'
             print(move, move_value)
             if move_value > best_value:
                 best_value = move_value
                 best_move = (i, j)
     return best_move

#### AI ENDS

class MoveViewSet(viewsets.ModelViewSet):
    queryset = Move.objects.all()
    serializer_class = MoveSerializer

    def create(self, request, *args, **kwargs):
        if request.method != 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # Check if the game is still on-going
        game_id = request.data.get('game')
        game = Game.objects.get(id=game_id)
        if game.game_outcome and game.game_outcome != 'going':
            return Response({"error": "The game has already ended."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Set the piece based on the is_tic_turn attribute of the game
        piece = 'X' if game.is_tic_turn else 'O'
        data = request.data.copy()
        data['piece'] = piece

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, piece=piece)
        headers = self.get_success_headers(serializer.data)
        game = serializer.instance.game
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, piece):
        print("user move")

        serializer.save(piece=piece)
        game = serializer.instance.game
        board = game.get_board()

        # Check for a win after the user's move
        winner = get_winner(board, game.grid_size)
        if winner == 'X':
            game.game_outcome = 'win'
            game.tic_user.total_games_played += 1
            game.tac_user.total_games_played += 1
            game.tic_user.total_games_won += 1
            game.tac_user.total_games_lost += 1
            game.tic_user.save()
            game.tac_user.save()
            game.save()
            print("win X")
            return
        if winner == 'O':
            game.game_outcome = 'lost'
            game.tic_user.total_games_played += 1
            game.tac_user.total_games_played += 1
            game.tac_user.total_games_won += 1
            game.tic_user.total_games_lost += 1
            game.tic_user.save()
            game.tac_user.save()
            game.save()
            print("win O")
            return
        if is_full(board, game.grid_size):
            game.game_outcome = 'draw'
            game.tic_user.total_games_played += 1
            game.tac_user.total_games_played += 1
            game.tic_user.save()
            game.tac_user.save()
            game.save()
            print("draw")
            return

        print("game is going")

        game.is_tic_turn = not game.is_tic_turn
        game.save()

        # AI makes a random move - TODO: AI must play as O
        if game.tac_user.username == "AI":
            print("AI starts")
            ai_move = find_best_move(board, game.grid_size,depth_limit=4)
            ai_move_str = f"{ai_move[0]},{ai_move[1]}"
            print(ai_move_str)
            Move.objects.create(game=game, move_number=serializer.instance.move_number + 1, move=ai_move_str, piece="O")

            # Update board after AI move
            board = game.get_board()
            game.is_tic_turn = not game.is_tic_turn
            game.save()

            # Check for a win after the AI's move
            winner = get_winner(board, game.grid_size)
            if winner == 'O':
                game.game_outcome = 'lose'
                game.tic_user.total_games_played += 1
                game.tac_user.total_games_played += 1
                game.tic_user.total_games_lost += 1
                game.tac_user.total_games_won += 1
                game.tic_user.save()
                game.tac_user.save()
                game.save()
            elif is_full(board, game.grid_size):
               print("draw")
               game.game_outcome = 'draw'
               game.tic_user.total_games_played += 1
               game.tac_user.total_games_played += 1
               game.tic_user.save()
               game.tac_user.save()
               game.save()


class GameBoardView(APIView):
     def get(self, request, game_id, format=None):
         step = request.query_params.get('step', None)
         if step is not None:
             try:
                 step = int(step)
             except ValueError:
                 return Response({"error": "Invalid step value."}, status=status.HTTP_400_BAD_REQUEST)

         game = Game.objects.get(id=game_id)
         board = game.get_board(step=step)
         response_data = {
             "game_id": game.id,
             "grid_size": game.grid_size,
             "tic_user": game.tic_user.username,
             "tac_user": game.tac_user.username,
             "tic_user_id": game.tic_user.id,
             "tac_user_id": game.tac_user.id,
             "is_tic_turn": game.is_tic_turn,
             "status": game.game_outcome,
             "total_moves":game.get_total_moves(),
             "board": board
         }
         return Response(response_data)

class BestPlayersView(APIView):
     def get(self, request, format=None):
         best_players = Player.objects.annotate(ratio=F('total_games_won') / (0.0001+F('total_games_lost'))).order_by('-ratio')[:20]
         serializer = PlayerSerializer(best_players, many=True)
         response_data = []

         for player in best_players:
             player_data = {
                 "id": player.id,
                 "username": player.username,
                 "total_games_played": player.total_games_played,
                 "total_games_won": player.total_games_won,
                 "total_games_lost": player.total_games_lost,
                 "win_loss_ratio": round(player.win_loss_ratio, 2)
             }
             response_data.append(player_data)

         return Response(response_data)
