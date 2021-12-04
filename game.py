import random
from flask_app.models import Game
import json


ROWS = 8
COLUMNS = 8

MELEE_MAX_HEALTH_POINTS = 10
RANGED_MAX_HEALTH_POINTS = 10
MAGE_MAX_HEALTH_POINTS = 10

MAGE_MAX_MANA_POINTS = 10

MAX_ACTION_POINTS = 2


def grid_map(rows=ROWS, columns=COLUMNS):
    data = []
    xpos = 1
    ypos = 1
    width = 50
    height = 50
    for row in range(rows):
        column_data = []
        for column in range(columns):
            tile = {'x': xpos,'y': ypos,'width': width, 'height': height, 'hero': 0}
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