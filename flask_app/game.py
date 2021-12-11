import random
from flask_app.models import Game, Hero
from flask_app import db
import json


ROWS = 8
COLUMNS = 8

MELEE_MAX_HEALTH_POINTS = 5
RANGED_MAX_HEALTH_POINTS = 3
MAGE_MAX_HEALTH_POINTS = 2


def populate_heroes():
    hero1 = Hero(hero_class='Melee', health_points=MELEE_MAX_HEALTH_POINTS, range=1, attack_damage=2)
    hero2 = Hero(hero_class='Ranger', health_points=RANGED_MAX_HEALTH_POINTS, range=2, attack_damage=1)
    hero3 = Hero(hero_class='Mage', health_points=MAGE_MAX_HEALTH_POINTS, range=3, attack_damage=1)
    db.session.add(hero1)
    db.session.commit()
    db.session.add(hero2)
    db.session.commit()
    db.session.add(hero3)
    db.session.commit()


def grid_map(rows=ROWS, columns=COLUMNS):
    data = []
    xpos = 1
    ypos = 1
    width = 50
    height = 50
    for row in range(rows):
        column_data = []
        for column in range(columns):
            tile = {'x': xpos, 'y': ypos, 'width': width, 'height': height, 'hero': 0}
            column_data.append(tile)
            xpos += width
        data.append(column_data)
        xpos = 1
        ypos += height
    return data


def spawn_heroes():
    Game.att_loc_x = 0
    Game.att_loc_y = random.randint(0, COLUMNS-1)

    Game.def_loc_x = ROWS-1
    Game.def_loc_y = random.randint(0, COLUMNS-1)


def new_game():
    game = Game(status=0, time=300)
    return game


# Player class to use in room
class Player:
    def __init__(self, name):
        self.name = name
        self.socket_id = None
        self.inactive = False
        self.health = None


# A game round
class Round:
    def __init__(self, players):
        self.players = players

# Room class
class Room:
    def __init__(self, id):
        self.id = id

        # Information about the room
        self.started = None
        self.player_round = None

        # The map of the game
        self.map = None

        # List of players in the room
        self.players = []
        self.connected = []

    # The room is full if it has 2 players
    def isFull(self):
        if len(self.players) == 2:
            return True
        return False

    # The room is available if it has less than 2 players and has not started
    def isReady(self):
        if len(self.players) < 2 and self.started is None:
            return True
        return False

    # The room has started the game
    def isStarted(self):
        if self.started is not None:
            return True
        return False

    # Adds a new player to the room
    def addPlayer(self, name):
        p = Player(name)
        if self.isReady():
            self.players.append(p)
        else:
            raise Exception('Game is not available.')
        return

    # Gets the names of the players in the room
    def getPlayers(self):
        names = []
        for p in self.players:
            names.append(p.name)
        return names

    # Gets a player in the room by name
    def getByName(self, name):
        for p in self.players:
            if p.name == name:
                return p
        return None

    # Gets a player in the room by id
    def getBySid(self, sid):
        for p in self.players:
            if p.socket_id == sid:
                return p
        return None

    # Gets the id of the player with the turn
    def getTurn(self):
        return self.player_round

    # Gets the map of the room
    def getMap(self):
        return self.map

    # Adds a player to the connected list and registers the id
    def connect(self, player, id):
        player.id = id
        self.connected.append(player)
        return

    # Removes a player from the connected list
    def disconnect(self, player):
        player.id = None
        if player in self.connected:
            self.connected.remove(player)
        return

