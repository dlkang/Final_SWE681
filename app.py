from flask import Flask, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>@localhost/<databasename>'  # The URI of the database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    lname = db.Column(db.String(120))
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name, lname, email, username, password):
        self.name = name
        self.lname = lname
        self.email = email
        self.username = username
        self.password = password


db.create_all()
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' #This is a security FLAW (cant hardcode secret keys) USED JUST AS A TEST


@app.route("/")
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        n_name = request.form['name']
        n_lname = request.form['lname']
        n_email = request.form['email']
        n_username = request.form['username']
        n_password = request.form['password']
        new_user = User(n_name, n_lname, n_email, n_username, n_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('hello.html', name=n_name) #Use as confirmation page for now
    else:
        return render_template("signup.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        n_user = User.query.filter_by(username=request.form['username']).first()
        if n_user.password == request.form['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
