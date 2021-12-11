from flask_app import create_app
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO(app)

import adventureGame

if __name__ == '__main__':
    socketio.run(app)
