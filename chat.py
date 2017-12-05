# https://www.youtube.com/watch?v=RdSrkkrj3l4
from flask import render_template, jsonify
from flask_socketio import SocketIO, send
from main import app, db

socketio = SocketIO(app)

class Chat_history(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    message = db.Column('message', db.String(500))
    conversation = db.Column('conversation', db.String(100))

# @app.route('/<conversation>')
@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    # print('Path: ' + jsonify(socketio))
    message = Chat_history(message=msg, conversation=socketio.path)
    db.session.add(message)
    db.session.commit()

    send(msg, broadcast=True)

@app.route('/chat/<conversation>')
def index(conversation):
    messages = Chat_history.query.filter_by(conversation=conversation)
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
        socketio.run(app)
