#!venv/bin/python

from flask_app import create_app
from flask_app.adventureGame import socketio
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

if __name__ == '__main__':
    socketio.run(app)