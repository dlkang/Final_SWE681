from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify
from flask_app import db
from flask_app.forms import RegistrationForm, LoginForm
from flask_app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug import security

import logging

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.route('/play', methods=['GET'])
def start_game():
    if current_user.is_authenticated:
        pass

@bp.route('/sendmove', methods=['POST'])
def validate_move():
    output_json = dict()

    data = request.get_json()
    reqKeys = {'player_id', 'attack', 'posX', 'posY'}
    if set(data.keys()) == reqKeys:
        print('Keys Match')
    else:
        #print(set(data.keys()))
        #print(reqKeys)
        return 'Invalid Move'

    output_json['player_id'] = data['player_id']

    if int(data['attack']) >= 0 and int(data['attack']) <= 100:
        output_json['attack'] = 'VALID'
    else:
        output_json['attack'] = 'INVALID'

    if int(data['posX']) >= 0 and int(data['posX']) <= 10:
        output_json['posX'] = 'VALID'
    else:
        output_json['posX'] = 'INVALID'

    if int(data['posY']) >= 0 and int(data['posY']) <= 10:
        output_json['posY'] = 'VALID'
    else:
        output_json['posY'] = 'INVALID'
    
    print("Data: ")
    print(data)
    print("OutputJson: ")
    print(output_json)
    return jsonify(output_json)

def process_move():
    pass
