import werkzeug.utils
from flask import Blueprint, redirect, render_template, request, url_for, flash, jsonify
from flask_app.game import grid_map, populate_heroes
from flask_app import db
from flask_app.models import Account, Game, Hero
from flask_app.forms import HeroForm
from flask_login import current_user
import json
from werkzeug import security

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.route('/hero', methods=['POST', 'GET'])
def hero():
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
                return redirect(url_for('game.queue_game'))
            else:
                print("Error selecting hero")
                render_template('hero.html', title='Hero Selection', form=form)
        return render_template('hero.html', title='Hero Selection', form=form)
    else:
        print("User not authenticated, please login")
        return redirect(url_for('auth.login'))



@bp.route('/queue', methods=['GET'])
def queue_game():
    #Check that the user is authenticated
    if current_user.is_authenticated:
        c_user_id = current_user.get_id()
        # Check if any user is in queue
        user_inqueue = Account.query.filter_by(queue_pos=1).first()
        if user_inqueue:
            #If user found, then get the user id, change queue to 0
            print("User found, with username " + user_inqueue.username)
            def_id = user_inqueue.id
            user_inqueue.queue_pos = 0
            db.session.commit()
            #Create the game in the database: we know att_id, def_id, the class and we just need to create the map!

            #Create the map
            grid = grid_map()
            grid_json = json.dumps(grid)
            data = {'grid': grid_json}
            #Start the game
            return render_template("game.html", title='PLAY', data=data)
        else:
            # If no user found, then introduce the user in queue by setting queue_pos value to 1
            print("No user found, entering queue")
            user = Account.query.filter_by(id=c_user_id).first()
            user.queue_pos = 1
            db.session.commit()
            #While in queue, keep searching for a game
            while(True):
                #If change in the queue_pos, then game was found! search for game, with def_id == your id
                if user.queue_pos == 0:
                    game = Game.query.filter_by(status=0, def_id=c_user_id).first()
    else:
        print("User not authenticated, please login")
        return redirect(url_for('auth.login'))


#@bp.route('/start', methods=['GET'])
#def start_game(def_id):



@bp.route('/checkmove', methods=['POST'])
def check_move():
    data = request.get_data()
    string_data = data.decode("utf-8")
    #TODO: perform security check
    if string_data == 'up':
        return 0
    elif string_data == 'down':
        return 1
    elif string_data == 'left':
        return 3
    elif string_data == 'right':
        return 2
    else:
        print("Erroneous input, quit game")
    print(string_data)
    return render_template("game.html", title='PLAY', data=data)
