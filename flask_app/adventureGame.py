
from flask import session,Blueprint, redirect, render_template, request, url_for, flash
from flask_app.game import grid_map, Room, populate_heroes, ROWS, COLUMNS
from flask_app import db
from flask_app.models import Account, Game, Hero, MoveList, MoveListScratch
from flask_app.forms import HeroForm
from flask_login import current_user
from flask_socketio import SocketIO, join_room, leave_room, close_room, emit, send
from random import choices
import datetime
import time
from uuid import uuid4


bp = Blueprint('game', __name__, url_prefix='/play')

@bp.route('/hero', methods=['POST', 'GET'])
def hero_select():
    if current_user.is_authenticated:
        #Populate hero table if not populated yet
        if Hero.query.count() == 0:
            print("Populating Hero table")
            populate_heroes()
        form = HeroForm()
        if form.validate_on_submit():
            form_hero = form.hero_class.data
            c_user_id = current_user.get_id()
            c_user = Account.query.filter_by(id=c_user_id).first()
            realhero = Hero.query.filter_by(hero_class=form_hero).first()
            if realhero:
                c_user.hero_class = realhero.hero_class
                db.session.commit()
                return redirect(url_for('game.join_game'))
            else:
                print("Error selecting hero")
                return render_template('hero.html', title='Hero Selection', form=form)
        return render_template('hero.html', title='Hero Selection', form=form)
    else:
        print("User not authenticated, please login")
        return redirect(url_for('auth.login'))



socketio = SocketIO(engineio_logger=True, logger=True, ping_timeout=5, async_mode='gevent')

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

    # Map is created and saved for room
    grid = grid_map()
    print("The map was added to the session")
    room = rooms.get(room_id)
    room.map = grid

    #Redirect to the room
    return redirect(url_for('game.game', room_id=room_id))

@bp.route('/joingame')
def join_game():
    if not current_user.is_authenticated:
        flash('You need to be logged in to join a game')
        return redirect(url_for("auth.login"))

    #Checks that the user has selected a hero
    c_user_id = current_user.get_id()
    c_user = Account.query.filter_by(id=c_user_id).first()
    c_user_hero = c_user.hero_class
    if c_user_hero is None:
        return redirect(url_for("game.hero_select"))

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
    print('Room has id ' + room_id)
    # Back to index if the room doesnt exist
    if room is None:
        flash('Game not found.')
        return redirect(url_for('index'))

    # Saves the room in the session
    session['room'] = room_id

    # Add the new player to the room if not already in it
    if current_user.username not in room.getPlayers():
        # Unless the room is full
        if room.isFull():
            flash('The game is full. Try another one.')
            return redirect(url_for('play.join_game'))
        room.addPlayer(current_user.username)

        if room.player1 is None:
            room.player1 = current_user.username
            room.player_turn = current_user.username
        else:
            room.player2 = current_user.username
        # Modify the value of the health of the player to match the class selected
        print("Health values modified")
        player = room.getByName(current_user.username)
        player.hero_class = current_user.hero_class
        hero = Hero.query.filter_by(hero_class=player.hero_class).first()
        player.health = hero.health_points
        player.range = hero.range
        player.dmg = hero.attack_damage
        player.precision = hero.precision

    return render_template('game.html')


# Socket connection event
@socketio.on('connect', namespace='/room')
def new_connection():
    if not current_user.is_authenticated:
        return False

    # Gets the room and player where the client is at from the session
    room = rooms.get(session['room'])
    print('\n\n%s\n' % (current_user.username))
    player = room.getByName(current_user.username)

    # Does nothing if the player has not already been added to the room
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


def start(room):
    room.started = 1
    player1 = room.getByName(room.player1)
    player2 = room.getByName(room.player2)
    data = {
        "player1": player1.name,
        "player1_class": player1.hero_class,
        "player2": player2.name,
        "player2_class": player2.hero_class,
        "player_turn": room.player_turn
    }
    emit('paint', room.map, namespace="/room", room=room)
    game_db(room)
    emit('start_game', data, namespace="/room", room=room)
    send("Starting the game", namespace='/room', room=room)
    return


def finish(room):
    winner = None
    loser = None
    # Updates the wins and losses for each player in the DB and clear the class selected
    for player in room.players:
        if player.health == 0:
            send("Game ended " + player.name + " lost", namespace='/room', room=room)
            loser = player.name
            user = Account.query.filter_by(username=player.name).first()
            emit('finish', {"message": "You lost!"}, namespace='/room', room=player.socket_id)
            user.losses = user.losses + 1
            user.hero_class = None
            db.session.commit()
        else:
            winner = player.name
            user = Account.query.filter_by(username=player.name).first()
            emit('finish', {"message": "You won!"}, namespace='/room', room=player.socket_id)
            user.wins = user.wins + 1
            user.hero_class = None
            db.session.commit()

    # Sets game status to finished
    game_p = Game.query.filter_by(room_id=room.id).first()
    game_p.status = 1
    game_p.winner = winner
    game_p.loser = loser
    db.session.commit()

    # Removes the room
    rooms.pop(session['room'])
    close_room(room)
    return


@socketio.on('game_move', namespace='/room')
def game_move(data):
    if not current_user.is_authenticated:
        print("User is not authenticated")
        return False

    # Get room from the session
    room = rooms.get(session['room'])
    if room is None:
        print("Cannot get room")
        return False

    # Checks that the sid corresponds to player socket_id
    player = room.getBySid(request.sid)
    if player not in room.players or player.name != current_user.username:
        print("SID doesnt correspond")
        return False

    # Checks that the room has started
    if not room.isStarted():
        emit('message', "Wait for other players to join", namespace='/room', room=request.sid)
        return False

    # Player cant make a move if its not their turn
    if player.name != room.player_turn:
        emit('message', "Not your turn!!", namespace='/room', room=request.sid)
        return False

    # Get position of player that made the move and validate it
    current_position = []
    other_position = []
    if player.name == room.player1:
        current_position = room.getHero1Pos()
        other_position = room.getHero2Pos()
    if player.name == room.player2:
        current_position = room.getHero2Pos()
        other_position = room.getHero1Pos()

    if not validate_move(data, current_position, other_position):
        emit('message', "That move is not valid", namespace='/room', room=request.sid)
        return False


    # Depending on the move, change position
    move_player(data, room, current_position)

    position_new = []
    if player.name == room.player1:
        position_new = room.getHero1Pos()

    if player.name == room.player2:
        position_new = room.getHero2Pos()

    send("User " + room.player_turn + " moved from tile x:" + str(current_position[0]+1) + ' y:' + str(current_position[1]+1) +
         " to x:" + str(position_new[0]+1) + " y:" + str(position_new[1]+1) + ".", namespace='/room', room=room)
    
    # Log move in move history
    new_move = MoveListScratch(timestamp=float(time.time()), game_id=room.getRoomId(), username_p1=room.player1, username_p2=room.player2, player_acting=room.player_turn, action=data)
    
    db.session.add(new_move)
    db.session.commit()

    # Change the turn of the player
    if room.player_turn == room.player1:
        room.player_turn = room.player2
    elif room.player_turn == room.player2:
        room.player_turn = room.player1
    send("Turn of player " + room.player_turn + " now", namespace='/room', room=room)
    emit('paint', room.map, namespace="/room", room=room)
    return


# Validates the moves according with the value and the room map
def validate_move(data, current_position, other_position):
    if data == 'right':
        if current_position[0] == (COLUMNS-1):
            return False
        if current_position[0]+1 == other_position[0] and current_position[1] == other_position[1]:
            return False
        return True
    if data == 'left':
        if current_position[0] == 0:
            return False
        if current_position[0]-1 == other_position[0] and current_position[1] == other_position[1]:
            return False
        return True
    if data == 'up':
        if current_position[1] == 0:
            return False
        if current_position[1]-1 == other_position[1] and current_position[0] == other_position[0]:
            return False
        return True
    if data == 'down':
        if current_position[1] == (ROWS-1):
            return False
        if current_position[1]+1 == other_position[1] and current_position[0] == other_position[0]:
            return False
        return True
    return False


# Makes the move in the map
def move_player(data, room, position):
    if data == 'right':
        if room.player_turn == room.player1:
            room.map[position[1]][position[0]]['hero1'] = 0
            room.map[position[1]][position[0]+1]['hero1'] = 1
        if room.player_turn == room.player2:
            room.map[position[1]][position[0]]['hero2'] = 0
            room.map[position[1]][position[0]+1]['hero2'] = 1
    if data == 'left':
        if room.player_turn == room.player1:
            room.map[position[1]][position[0]]['hero1'] = 0
            room.map[position[1]][position[0]-1]['hero1'] = 1
        if room.player_turn == room.player2:
            room.map[position[1]][position[0]]['hero2'] = 0
            room.map[position[1]][position[0]-1]['hero2'] = 1

    if data == 'up':
        if room.player_turn == room.player1:
            room.map[position[1]][position[0]]['hero1'] = 0
            room.map[position[1]-1][position[0]]['hero1'] = 1
        if room.player_turn == room.player2:
            room.map[position[1]][position[0]]['hero2'] = 0
            room.map[position[1]-1][position[0]]['hero2'] = 1

    if data == 'down':
        if room.player_turn == room.player1:
            room.map[position[1]][position[0]]['hero1'] = 0
            room.map[position[1]+1][position[0]]['hero1'] = 1
        if room.player_turn == room.player2:
            room.map[position[1]][position[0]]['hero2'] = 0
            room.map[position[1]+1][position[0]]['hero2'] = 1

    return


@socketio.on('game_attack', namespace="/room")
def game_attack():
    if not current_user.is_authenticated:
        print("User is not authenticated")
        return False

    # Get room from the session
    room = rooms.get(session['room'])
    if room is None:
        print("Cannot get room")
        return False

    # Checks that the sid corresponds to player socket_id
    player = room.getBySid(request.sid)
    if player not in room.players or player.name != current_user.username:
        print("SID doesnt correspond")
        return False

    # Checks that the room has started
    if not room.isStarted():
        emit('message', "Wait for other players to join", namespace='/room', room=request.sid)
        return False

    # Player cant make a move if its not their turn
    if player.name != room.player_turn:
        emit('message', "Not your turn!!", namespace='/room', room=request.sid)
        return False

    # Get enemy, position of both players
    ally_pos = []
    enemy_pos = []
    enemy = None
    if player.name == room.player1:
        ally_pos = room.getHero1Pos()
        enemy_pos = room.getHero2Pos()
        enemy_player = room.player2
        enemy = room.getByName(enemy_player)
    if player.name == room.player2:
        ally_pos = room.getHero2Pos()
        enemy_pos = room.getHero1Pos()
        enemy_player = room.player1
        enemy = room.getByName(enemy_player)
    attack_range = player.range

    if not validate_attack(attack_range, ally_pos, enemy_pos):
        emit('message', "The enemy is not within range", namespace='/room', room=request.sid)
        return False

    if enemy is None:
        return False

    # Attack another player
    attack_player(room, player, enemy)

    send("The remaining health of player " + player.name + " is " + str(player.health), namespace='/room', room=room)
    send("The remaining health of player " + enemy.name + " is " + str(enemy.health), namespace='/room', room=room)

    # Check the health of both players
    if enemy.health <= 0:
        finish(room)
        return True

    # Change the turn of the player
    if room.player_turn == room.player1:
        room.player_turn = room.player2
    elif room.player_turn == room.player2:
        room.player_turn = room.player1
    send("Turn of player " + room.player_turn + " now", namespace='/room', room=room)



    return


# Validate that the enemy is within range
def validate_attack(attack_range, ally_pos, enemy_pos):
    if ally_pos[0] > enemy_pos[0]:
        if ally_pos[1] > enemy_pos[1]:
            x_dis = ally_pos[0]-enemy_pos[0]
            y_dis = ally_pos[1]-enemy_pos[1]
            if x_dis <= attack_range and y_dis <= attack_range:
                return True
            return False
        else:
            x_dis = ally_pos[0]-enemy_pos[0]
            y_dis = enemy_pos[1]-ally_pos[1]
            if x_dis <= attack_range and y_dis <= attack_range:
                return True
            return False
    else:
        if ally_pos[1] > enemy_pos[1]:
            x_dis = enemy_pos[0]-ally_pos[0]
            y_dis = ally_pos[1]-enemy_pos[1]
            if x_dis <= attack_range and y_dis <= attack_range:
                return True
            return False
        else:
            x_dis = enemy_pos[0]-ally_pos[0]
            y_dis = enemy_pos[1]-ally_pos[1]
            if x_dis <= attack_range and y_dis <= attack_range:
                return True
            return False

def attack_player(room, player, enemy):
    #Precision check
    damage_list = [player.dmg, 0]
    precision_distribution = [player.precision, 1-player.precision]
    damage = choices(damage_list, precision_distribution)

    if damage[0] == 0:
        send("User " + player.name + " failed the attack.", namespace='/room', room=room)
        attack_string = "%s missed attacking %s" % (player.name, enemy.name)
        new_move = MoveListScratch(timestamp=float(time.time()), game_id=room.getRoomId(), username_p1=room.player1, username_p2=room.player2, player_acting=player, action=attack_string)
        db.session.add(new_move)
        db.session.commit()
    else:
        remaining_health = enemy.health - damage[0]
        if remaining_health < 0:
            remaining_health = 0
        enemy.health = remaining_health
        send("User " + player.name + " attacked " + enemy.name + " and did " + str(damage[0]) + " damage!",
             namespace='/room', room=room)
        attack_string = "%s attacked %s" % (player.name, enemy.name)
        new_move = MoveListScratch(timestamp=float(time.time()), game_id=room.getRoomId(), username_p1=room.player1, username_p2=room.player2, player_acting=player, action=attack_string)
        
        db.session.add(new_move)
        db.session.commit()
    return

@bp.route('/past_games', methods=['GET'])
def display_games():
    games = []
    if not current_user.is_authenticated:
        print("user not authenticated, please login")
        return redirect(url_for('auth.login'))
    
    queried_games = Game.query.filter_by(status=1).order_by(Game.room_id)

    games = [[game.room_id, game.att_name, game.def_name, game.winner, game.loser] for game in queried_games]

    return render_template('past_games.html', games=games)

@bp.route('/moves')
def display_moves():
    moves = []

    if not current_user.is_authenticated:
        print("user not authenticated, please login")
        return redirect(url_for('auth.login'))
    
    queried_moves = MoveListScratch.query.order_by(MoveListScratch.timestamp)

    moves = [[move.timestamp, move.game_id, move.username_p1, move.username_p2, move.player_acting, move.action] for move in queried_moves]

    return render_template('moves.html', moves=moves)

def game_db(room):
    room_id = room.id
    p1 = room.player1
    p2 = room.player2
    player1 = room.getByName(p1)
    player2 = room.getByName(p2)
    p1_hero = player1.hero_class
    p2_hero = player2.hero_class
    game = Game(room_id=room_id, att_name=p1, def_name=p2, att_class=p1_hero, def_class=p2_hero)
    list_players = room.getPlayers()
    for player in list_players:
        p = room.getByName(player)
        user = Account.query.filter_by(username=p.name).first()
        game.players.append(user)
    db.session.add(game)
    db.session.commit()
