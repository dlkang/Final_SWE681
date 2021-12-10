from flask import Flask, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_app.config import Config

import sqlalchemy

db = SQLAlchemy()
log_man = LoginManager()
log_man.login_view = 'login'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    log_man.init_app(app)

    from flask_app import auth
    app.register_blueprint(auth.bp)

    from flask_app import adventureGame
    app.register_blueprint(adventureGame.bp)
    
    with app.app_context():
        db.create_all()
        db.session.commit()

    @app.route("/")
    @app.route("/index")
    @app.route("/home")
    def index():
        print('inSession')
        print(session)
        if 'username' in session:
            print('inUsername')
            return render_template("index.html", username=session['username'], title='Home')
        return render_template("index.html", title='Home')

    return app
