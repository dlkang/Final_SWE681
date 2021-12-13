from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app.models import Account, Hero


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), Length(min=8, max=20),
                                                 EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Account.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Choose another one.')

    def validate_email(self, email):
        user = Account.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Choose another one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class HeroForm(FlaskForm):
    classes = ['Melee', 'Ranger', 'Mage']
    hero_class = SelectField('Hero Class', choices=classes, validators=[DataRequired()])
    submit = SubmitField('Start Game')
