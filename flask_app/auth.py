from flask import Blueprint, redirect, render_template, url_for, flash
from flask_app import db, log_man
from flask_app.forms import RegistrationForm, LoginForm
from flask_app.models import Account
from flask_login import current_user, login_user, logout_user
from werkzeug import security
import re


bp = Blueprint('auth', __name__, url_prefix='/auth')


@log_man.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

# Register function
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Checks that user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    # Validate the form with the form.py requirements
    if form.validate_on_submit():
        usern = form.username.data
        pwd = form.password.data
        email = form.email.data

        # Perform security checks
        # Username between 3 and 20 characters
        if not re.search('^[a-zA-Z0-9]{3,20}$', usern):
            flash('Username must be between 3 and 20 characters')
            return render_template("register.html", title='Registration', form=form)

        # Passwords between 8 and 20 characters
        if not re.search('^[a-zA-Z0-9@_!]{8,20}$', pwd):
            flash('Password must be between 8 and 20 characters')
            return render_template("register.html", title='Registration', form=form)

        # Email must look like an email
        if not re.search('^[a-zA-Z0-9]+@[a-z]+.[a-z]{1,3}$', email):
            flash('Email must be in email form')
            return render_template("register.html", title='Registration', form=form)

        # Hash the password
        hashed_pwd = security.generate_password_hash(pwd)
        new_user = Account(username=usern, password=hashed_pwd, email=email)
        print("Registration valid, user registered " + new_user.username)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful, you are now able to log in", "success")
        return redirect(url_for('auth.login'))
    else:
        print("Registration not valid")
        return render_template("register.html", title='Registration', form=form)

# Login function
@bp.route('/login', methods=['POST', 'GET'])
def login():

    # Checks that user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()

    # Validate the form with the form.py requirements
    if form.validate_on_submit():
        usern = form.username.data
        pwd = form.password.data

        # Perform security checks
        # Username between 3 and 20 characters
        if not re.search('^[a-zA-Z0-9]{3,20}$', usern):
            flash('Username must be between 3 and 20 characters')
            return render_template("register.html", title='Registration', form=form)

        # Passwords between 8 and 20 characters
        if not re.search('^[a-zA-Z0-9@_!]{8,20}$', pwd):
            flash('Password must be between 8 and 20 characters')
            return render_template("register.html", title='Registration', form=form)

        user = Account.query.filter_by(username=usern).first()
        if user and security.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
    print("Form not valid")
    return render_template('login.html', title='Login', form=form)


# Logout function
@bp.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))

    # Logout user
    logout_user()
    return redirect(url_for('index'))
