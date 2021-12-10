from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_app import db
from flask_app.forms import RegistrationForm, LoginForm
from flask_app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug import security

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = security.generate_password_hash(form.password.data)
        print(hashed_pwd)
        new_user = User(username=form.username.data, password=hashed_pwd, email=form.email.data, queue_pos=None)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful, you are now able to log in", "success")
        return redirect(url_for('auth.login'))
    else:
        print("FALLO!!")
        return render_template("register.html", title='Registration', form=form)


@bp.route('/login', methods=['POST', 'GET'])
def login():
    print('logging in')
    if current_user.is_authenticated:
        print('Authenticated User')
        return redirect(url_for("index"))
    form = LoginForm()
    user = User.query.filter_by(username=form.username.data).first()
    if user and security.check_password_hash(user.password, form.password.data):
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        # if not is_safe_url(next)  -> need to create function to check safe links or just hardcode it in the system
        return redirect(next_page) if next_page else redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
