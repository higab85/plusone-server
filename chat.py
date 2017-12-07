# https://www.youtube.com/watch?v=RdSrkkrj3l4
from flask import render_template, request
from flask_socketio import SocketIO, send, emit
from main import app, db

socketio = SocketIO(app)
num_users = 0
addedUser = False
session = {}

class Chat_history(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    message = db.Column('message', db.String(500))
    conversation = db.Column('conversation', db.String(100))


@socketio.on('add user')
def on_add_user(username):
    global addedUser, num_users
    session['username'] = username

    # messages = Chat_history.query.all() # filter_by(conversation=conversation)

    if addedUser:
        num_users+=1
    addedUser = True
    emit('login', {
        'numUsers':num_users
        })
    # for message in messages:
    #     emit('')
    emit('user joined', {
        'username': session['username'],
        'numUsers': num_users
    }, broadcast=True)

@socketio.on('typing')
def on_typing():
     emit('typing', {'username':session['username']})

@socketio.on('stop typing')
def stop_typing():
    emit('stop typing', {'username':session['username']})

@socketio.on('disconnect')
def on_disconnect():
    global addedUser, num_users
    if addedUser:
         num_users-=1
    emit('user left', {'username':session['username']})

# @app.route('/<conversation>')
@socketio.on('new message')
def handleMessage(data):
    emit('new message', {
        'username':session['username'],
        'message':data
    })

    message = Chat_history(message=data)
    db.session.add(message)
    db.session.commit()

@app.route('/')
def index():
    messages = Chat_history.query.all() #.filter_by(conversation=conversation)
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
        socketio.run(app)
