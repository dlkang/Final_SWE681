
from flask import session,Blueprint, redirect, render_template, request, url_for, flash
from flask_app.game import grid_map, Room, populate_heroes
from flask_app import db
from flask_app.models import Account, Game, Hero
from flask_app.forms import HeroForm
from flask_login import current_user
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit, send
import json
import time
from uuid import uuid4


bp = Blueprint('game', __name__, url_prefix='/play')

@bp.route('/hero', methods=['POST', 'GET'])
def hero_select():
    if current_user.is_authenticated:
        #Populate hero table
        if Hero.query.count() == 0:
            print("Populating Hero table")
            populate_heroes()
        form = HeroForm()
        if form.validate_on_submit():
            form_hero = form.hero_class.data
            print(form_hero)
            c_user_id = current_user.get_id()
            c_user = Account.query.filter_by(id=c_user_id).first()
            realhero = Hero.query.filter_by(hero_class=form_hero).first()
            if realhero:
                c_user.hero_class = realhero.hero_class
                db.session.commit()
                return render_template("lobby.html")
            else:
                print("Error selecting hero")
                render_template('hero.html', title='Hero Selection', form=form)
        return render_template('hero.html', title='Hero Selection', form=form)
    else:
        print("User not authenticated, please login")
        return redirect(url_for('auth.login'))


socketio = SocketIO()

# List of active games to join
rooms = {}

@bp.route('/newgame')
def create_game():
    if not current_user.is_authenticated:
        flash('You need to be logged in to create a game')
        return redirect(url_for("auth.login"))

    #create game identifier and check it doesnt exist
    room_id = str(uuid4().int)
    if room_id in rooms:
        raise Exception("Games with the same ID cant exist")

    rooms[room_id] = Room(room_id)

    #Redirect to the room
    return redirect(url_for('game.game', room_id=room_id))

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
@bp.route('/game/<room_id>')
def game(room_id):
    if not current_user.is_authenticated:
        flash('You need to login first.')
        return redirect(url_for('auth.login'))

    # Gets the room object from the active rooms dictionary
    room = rooms.get(room_id)
    print('Room created has id ' + room_id)
    # Back to index if the room doesnt exist
    if room is None:
        flash('Game not found.')
        return redirect(url_for('index'))

    # Saves the room in the session
    session['room'] = room_id

    # Add the new player to the room
    if current_user.username not in room.getPlayers():
        # Unless the room is full
        if room.isFull():
            flash('The game is full. Try another one.')
            return redirect(url_for('play.join_game'))
        room.addPlayer(current_user.username)

        # Modify the value of the health of the player to match the class selected
        player = room.getByName(current_user.username)
        player.hero_class = current_user.hero_class
        hero = Hero.query.filter_by(hero_class=player.hero_class).first()
        player.health = hero.health_points

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
    print("A player has joined the room")
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
    print("Starting the game")
    #Map is created and saved for room
    grid = grid_map()
    grid_json = json.dumps(grid)
    map_data = {'grid': grid_json}

    room.map = map_data['grid']

    for player in room.players:
        emit('start_game', data=map_data, namespace="/room", room=player.socket_id)
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
