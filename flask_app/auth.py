from flask import Blueprint, session, redirect, render_template, request, url_for
from flask_app import db
from flask_app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # NEED TO CHECK FOR PARAMETERS NOT NULL!!!
        # AND MORE SECURITY CHECKS!!!
        n_name = request.form['name']
        n_lname = request.form['lname']
        n_email = request.form['email']
        n_username = request.form['username']
        n_password = request.form['password']
        new_user = User(n_name, n_lname, n_email, n_username, n_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('index.html', name=n_name) #Use as confirmation page for now
    else:
        return render_template("register.html")


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
    #NEED TO CHECK FOR PARAMETERS NOT NULL!!!
    #AND MORE SECURITY CHECKS!!!
        n_user = User.query.filter_by(username=request.form['username']).first()
        if n_user.password == request.form['password']:
            session['username'] = request.form['username']
            return render_template('index.html', username=session['username'])
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
