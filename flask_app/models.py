from flask_app import db, log_man
from flask_login import UserMixin

@log_man.user_loader
def load_user(account_id):
    return Account.query.get(int(account_id))

players = db.Table('players',
                db.Column('account_id', db.Integer, db.ForeignKey('account.id'), primary_key=True),
                db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True))


class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    wins = db.Column(db.Integer, unique=False, nullable=False, default=0)
    losses = db.Column(db.Integer, unique=False, nullable=False, default=0)
    queue_pos = db.Column(db.Integer, nullable=False, default=0)
    hero_class = db.Column(db.String(20), nullable=True)
    games = db.relationship('Game', secondary=players, backref=db.backref('players', lazy=True), lazy='subquery')


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(120), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    winner = db.Column(db.String(20), nullable=True)
    loser = db.Column(db.String(20), nullable=True)
    att_name = db.Column(db.String(20), nullable=False)
    def_name = db.Column(db.String(20), nullable=False)
    att_class = db.Column(db.String(20), unique=False)
    def_class = db.Column(db.String(20), unique=False)


class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_class = db.Column(db.String(20), nullable=False)
    health_points = db.Column(db.Integer, nullable=False)
    attack_damage = db.Column(db.Integer, nullable=False)
    range = db.Column(db.Integer, nullable=False)
    precision = db.Column(db.Float, nullable=False)


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), nullable=False)
    movement = db.Column(db.Text, nullable=True)
    attack = db.Column(db.Integer, nullable=True)
    range = db.Column(db.Text, nullable=True)

class MoveList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    game_id = db.Column(db.String(100), nullable=False)
    username_p1 = db.Column(db.String(120), nullable=False)
    username_p2 = db.Column(db.String(120), nullable=False)
    player_acting = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(100), nullable=False)

class MoveListScratch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float, nullable=False)
    game_id = db.Column(db.String(100), nullable=False)
    username_p1 = db.Column(db.String(120), nullable=False)
    username_p2 = db.Column(db.String(120), nullable=False)
    player_acting = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(100), nullable=False)
