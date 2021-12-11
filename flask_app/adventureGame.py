
from flask import session,Blueprint, redirect, render_template, request, url_for, flash, jsonify
from flask_app.game import grid_map, Room, Player
from flask_app import db
from flask_app.models import Account, Game, Hero
from flask_app.forms import HeroForm
from flask_login import current_user
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit, send
import json
from datetime import datetime
import time
from uuid import uuid4


bp = Blueprint('game', __name__, url_prefix='/play')

socketio = SocketIO()

# List of active games to join
rooms = {}

@bp.route('/newgame')
def create_game():
    if not current_user.is_authenticated:
        flash('You need to be logged in to create a game')
        return redirect(url_for("auth.login"))

    #create game identifier and check it doesnt exist
    id = str(uuid4().int)
    if id in rooms:
        raise Exception("Games with the same ID cant exist")

    rooms[id] = Room(id)

    #Redirect to the room
    return redirect(url_for('game.room', id=id))

@bp.route('/joingame')
def join_game():
    if not current_user.is_authenticated:
        flash('You need to be logged in to join a game')
        return redirect(url_for("auth.login"))

    # Get a list of all the rooms ready to be joined
    ready = []

    for room in rooms.values():
        if room.isReady():
            ready.append((room.id, room.getPlayers()))

    return render_template('lobby.html', rooms=ready)


# Game room function: where the game occurs
@bp.route('/game/<id>')
def game(id):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the room object from the active rooms dictionary
    room = rooms.get(id)

    # Back to index if the room doesnt exist anymore
    if room is None:
        flash('Game not found.')
        return redirect(url_for('index'))

    # Saves the room in the session
    session['room'] = id

    # Add the new player to the room
    if current_user.username not in room.getPlayers():
        # Unless the room is full
        if room.isFull():
            flash('The game is full. Try another one.')
            return redirect(url_for('play.join_game'))
        room.addPlayer(current_user.username)

    return render_template('game.html')


# Socket connection event
@socketio.on('connect', namespace='/room')
def new_connection():
    if not current_user.is_authenticated:
        return False

    # Gets the room and player where the client is at from the session
    room = rooms.get(session['room'])
    player = room.getByName(current_user.username)

    # Does nothing if the player has not already been added to the room
    # or if the player is already connected
    if player is None or player in room.connected:
        return False

    # Stores the connection session_id for the player
    room.connect(player, request.sid)

    # Adds the player to the room so that it receives events
    join_room(room)

    # If player was just inactive
    if room.isStarted():
        return True

    # Sends connection to all players in room
    send("User {} has connected.".format(player.name), namespace='/room', room=room)

    # If room has all players, start the game
    if room.isFull():
        start(room)
    return


# Socket disconnection event
@socketio.on('disconnect', namespace='/room')
def new_disconnection():

    room = rooms.get(session['room'])
    if room is None:
        return

    #Obtain the player identity
    player = room.getBySid(request.sid)
    if player is None:
        return

    # The player is removed from the connected players and from room
    room.disconnect(player)
    leave_room(room)

    # If the game has started
    if room.isStarted():
        # It waits 60 seconds for a reconnection
        time.sleep(60)

        # If after that time the player has not reconnected
        if player not in room.connected:
            send("User {} was afk for too long.".format(player.name), namespace='/room', room=room)

            # TODO The player loses the game IMPLEMENT IT
            player.health = 0
            # The game ends
            finish(room)
            return
        return

    # If the game hasn't started, the player is removed from the players list
    room.players.remove(player)
    send("User {} has disconnected.".format(player.name), namespace='/room', room=room)

    # If there are no players in a room, game is removed
    if len(room.players) == 0:
        rooms.pop(session['room'])
    return


#TODO Game start
def start(room):
    #Map is created
    grid = grid_map()
    grid_json = json.dumps(grid)
    map = {'grid': grid_json}

    #Database is initialized
    #start_db(room)
    return


def finish(room):
    # Checks the player health to check who won
    for player in room.players:
        if player.health == 0:
            msg = "Game ended " + player.name + " lost"
            send(msg, namespace='/room', room=room)

            # Updates the wins and losses for each player in the DB
            user = Account.query.filter_by(username=player.name).first()
            emit('finish', {"message": "You lost!"}, namespace='/room', room=player.sid)
            user.losses = user.losses + 1
        else:
            # Updates the wins and losses for each player in the DB
            user = Account.query.filter_by(username=player.name).first()
            emit('finish', {"message": "You won!"}, namespace='/room', room=player.sid)
            user.wins = user.wins + 1

    # Sets game status to finished
    game = Game.query.filter_by(room_id=room.id).first()
    game.status = 2
    db.session.commit()

    # Removes the room
    rooms.pop(session['room'])
    close_room(room)
    return
