from flask_app import db, log_man
from flask_login import UserMixin



@log_man.user_loader
def load_user(account_id):
    return Account.query.get(int(account_id))

play = db.Table('play',
                db.Column('id', db.Integer, primary_key=True),
                db.Column('account_id', db.Integer, db.ForeignKey('account.id'), unique=False),
                db.Column('game_id', db.Integer, db.ForeignKey('game.id'), unique=False))


class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    wins = db.Column(db.Integer, unique=False, nullable=False, default=0)
    loses = db.Column(db.Integer, unique=False, nullable=False, default=0)
    queue_pos = db.Column(db.Integer, nullable=False, default=0)
    hero_class = db.Column(db.String(20), nullable=True)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer, nullable=False)
    winner = db.Column(db.Integer, nullable=True)
    loser = db.Column(db.Integer, nullable=True)
    time = db.Column(db.Integer, nullable=False)
    player_turn = db.Column(db.Integer, nullable=False)
    att_id = db.Column(db.Integer, nullable=False)
    def_id = db.Column(db.Integer, nullable=False)
    att_class = db.Column(db.String(20), unique=False)
    def_class = db.Column(db.String(20), unique=False)
    att_hp = db.Column(db.Integer, nullable=False)
    def_hp = db.Column(db.Integer, nullable=False)
    att_loc_x = db.Column(db.Integer, nullable=False)
    att_loc_y = db.Column(db.Integer, nullable=False)
    def_loc_x = db.Column(db.Integer, nullable=False)
    def_loc_y = db.Column(db.Integer, nullable=False)
    map = db.Column(db.Text, nullable=False)
    players = db.relationship('Account', secondary=play, backref=db.backref('games', lazy=True), lazy='subquery')


class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_class = db.Column(db.String(20), nullable=False)
    health_points = db.Column(db.Integer, nullable=False)
    attack_damage = db.Column(db.Integer, nullable=False)
    range = db.Column(db.Integer, nullable=False)


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), nullable=False)
    movement = db.Column(db.Text, nullable=True)
    attack = db.Column(db.Integer, nullable=True)
    range = db.Column(db.Text, nullable=True)
