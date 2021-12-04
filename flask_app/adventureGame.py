from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify
from flask_app.game import grid_map
import json
from werkzeug import security

bp = Blueprint('game', __name__, url_prefix='/game')


@bp.route('/start', methods=['GET'])
def start_game():
    grid = grid_map()
    grid_json = json.dumps(grid)
    data = {'grid': grid_json}
    return render_template("game.html", title='PLAY', data=data)


@bp.route('/sendmove', methods=['POST'])
def validate_move():
    output_json = dict()

    data = request.get_json()
    reqKeys = {'player_id', 'attack', 'posX', 'posY'}
    if set(data.keys()) == reqKeys:
        print('Keys Match')
    else:
        # print(set(data.keys()))
        # print(reqKeys)
        return 'Invalid Move'

    output_json['player_id'] = data['player_id']

    if int(data['attack']) >= 0 and int(data['attack']) <= 100:
        output_json['attack'] = 'VALID'

    if int(data['posX']) >= 0 and int(data['posX']) <= 10:
        output_json['posX'] = 'VALID'

    if int(data['posY']) >= 0 and int(data['posY']) <= 10:
        output_json['posY'] = 'VALID'

    print("Data: ")
    print(data)
    print("OutputJson: ")
    print(output_json)
    return jsonify(output_json)
