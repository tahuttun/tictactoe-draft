# Tic Tac Toe Django App

This is a simple Tic Tac Toe web application developed using Django, Django Rest Framework, SQLite3 and Vue. Most of the code and documentation were created using ChatGPT4 and ChatBlade, mainly for educational purposes. This project addresses the code challenge at https://twoday.fi/koodihaaste. The app has limited functionality and primarily aims to adhere to the challenge guidelines.


# Main Features
* Create and join games
* Play against other users or an AI opponent
* View game history and board state at any point in the game
* View leaderboard of best players based on win-loss ratio

# Frameworks and Libraries
* Django: A high-level Python web framework that enables rapid development of secure and maintainable websites.
* Django Rest Framework: A powerful and flexible toolkit for building Web APIs.
* SQLite3: A C library that provides a lightweight disk-based database that doesn't require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language.
* Vue.js frontend


# Installation
 * git clone https://github.com/tahuttun/tictactoe-draft.git
 * cd tictactoe-draft
 * pip3 install -r requirements.txt
 * python3 manage.py migrate
 * python3 manage.py makemigrations
 
# Run the server (tested with Ubuntu)
python manage.py runserver

The application should now be running at http://localhost:8000/static/index.html.

# Usage
*  Start a new game or join an existing one. For an AI opponent, name Player2 as "AI."
*  Play the game by clicking on the board cells.
*  View the game history and board state at any point in the game.
*  Check the leaderboard to see the best players based on their win-loss ratio.

# API Endpoints
 *  /api/players/: List all players or create a new player.
 *  /api/games/: List all games or create a new game.
 *  /api/moves/: List all moves or create a new move.
 *  /api/best-players/: List the top 20 players based on their win-loss ratio.
 *  /api/games/<int:game_id>/board/: Get the board state of a specific game.
 *  /api/games/<int:game_id>/delete/: Delete a specific game.

# Screenshot

![Image](https://raw.githubusercontent.com/tahuttun/tictactoe-draft/main/2023-05-01%2020_36_16-Window.png)
