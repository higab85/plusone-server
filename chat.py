# https://www.youtube.com/watch?v=RdSrkkrj3l4
from flask import render_template, request, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from main import app, db
import math

socketio = SocketIO(app)
num_users = 0
addedUser = False

class Chat_history(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    message = db.Column('message', db.String(500))
    conversation = db.Column('conversation', db.String(100))
    username = db.Column('user', db.String(100))

@socketio.on('join')
def on_join(data):
    global addedUser, num_users
    # print('recieved: ' + str(data))
    session['username'] = data['username']
    # print('username: ' , username)
    session['room'] = str(data['room'])
    print("User '" + session['username'] + "' conected to room " + session['room'] + " addedUser:" + str(addedUser))
    join_room(session['room'])
    print("username: " + session['username'] + ", numUsers: " + str(num_users) + "is joining")
    emit('user joined', {
        'username': session['username'],
        'numUsers': str(num_users)
    }, room=room)
    num_users+=1
    messages = Chat_history.query.filter_by(conversation=session['room'])
    for message in messages:
        emit('new message', {
        'username':message.username,
        'message':message.message
    }, room=session['room'])



@socketio.on('typing')
def on_typing():
    print(username + " is typing")
    emit('typing', {'username':session['username']}, room=session['room'])

@socketio.on('stop typing')
def stop_typing():
    emit('stop typing', {'username':session['username']}, room=session['room'])

@socketio.on('disconnect')
def on_disconnect():
    global addedUser, num_users
    # if addedUser:
    #      num_users-=1
    # emit('user left', {'username':session['username']})
    room = session.get('room')
    leave_room(session['room'])
    print("username: " + session['username'] + ", numUsers: " + str(num_users) + "is leaving")
    num_users-=1
    emit('user joined', {
        'username':session['username'],
        'numUsers': str(num_users)
    }, room=session['room'])

# @app.route('/<conversation>')
@socketio.on('new message')
def handleMessage(data):
    emit('new message', {
        'username':session['username'],
        'message':data
    }, room=room)
    print("saving '" + data + "' from user '" + session['username'] + "' to room " + session['room'])
    message = Chat_history(message=data, username=session['username'], conversation=session['room'])
    db.session.add(message)
    db.session.commit()

@app.route('/')
def index():
    messages = Chat_history.query.all() #.filter_by(conversation=conversation)
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
        socketio.run(app)
