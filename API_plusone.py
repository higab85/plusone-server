# https://www.youtube.com/watch?v=WxGBoY5iNXY
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.session import _SessionClassMethods
import jwt
import datetime
from functools import wraps

# from sqlalchemy import Table, Column, Integer, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

app = Flask(__name__)

app.config['SECRET_KEY'] = "mysecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@localhost/plusone'

db = SQLAlchemy(app)


# users_attending_events = Table('users_attending_events', Base.metadata,
#     Column('user_id', Integer, ForeignKey('User.id')),
#     Column('event_id', Integer, ForeignKey('Event.id'))
# )
users_attending_events = db.Table('users_attending_events', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')))

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    attending_events = db.relationship(
        'Event',
        secondary=users_attending_events,
        lazy="dynamic",
        backref="attendees")


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.String(50))
    name = db.Column(db.String(50))
    description = db.Column(db.String(500))
    start = db.Column(db.String(50))
    end = db.Column(db.String(50))
    type = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# NOTE: FOR DEBUG ONLY, NOT FOR PRODUCTION
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['email'] = user.email
        output.append(user_data)
    return jsonify({'users': output})

# NOTE: FOR DEBUG ONLY, NOT FOR PRODUCTION
@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message':'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['email'] = user.email

    return jsonify(user_data)


# TODO: Handle error when email already exists
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New user created!'})

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(email=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=2) }, app.config['SECRET_KEY'])

        return jsonify({'token' : token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/event', methods=['GET'])
@token_required
def get_all_events(current_user):
    events = Event.query.filter_by(user_id=current_user.id)

    output = []
    for event in events:
        event_data = {}
        event_data['id'] = event.id
        event_data['user_id'] = event.user_id
        event_data['name'] = event.name
        event_data['description'] = event.description
        event_data['start'] = event.start
        event_data['end'] = event.end
        event_data['type'] = event.type
        event_data['latitude'] = event.latitude
        event_data['longitude'] = event.longitude
        output.append(event_data)

    return jsonify(output)

@app.route('/event/<event_id>', methods=['GET'])
@token_required
def get_one_event(current_user, event_id):
    event = Event.query.filter_by(id=event_id).first()

    if not event:
        return jsonify({'message' : 'No event found'})

    # query = User.query.filter(User.id==user_id, User.attending_events.contains(event))


    event_data = {}
    event_data['id'] = event.id
    event_data['user_id'] = event.user_id
    event_data['name'] = event.name
    event_data['description'] = event.description
    event_data['start'] = event.start
    event_data['end'] = event.end
    event_data['type'] = event.type
    event_data['latitude'] = event.latitude
    event_data['longitude'] = event.longitude

    event_data['subscribed'] =  db.session.query(db.session.query(User).filter(event in set(current_user.attending_events.all())).exists()).scalar()

    # event_data['attending'] = users_attending_events.user_id.filter(current_user.id) event_id=event_id).first() != None

    return jsonify(event_data)

@app.route('/event', methods=['POST'])
@token_required
def create_event(current_user):
    data = request.get_json()

    new_event = Event(
        public_id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=data['name'],
        description=data['description'],
        start=data['start'],
        end=data['end'],
        type=data['type'],
        latitude=data['latitude'],
        longitude=data['longitude'])

    db.session.add(new_event)
    db.session.commit()

    return jsonify({'message' : 'event created.'})

@app.route('/event/<event_id>', methods=['POST'])
@token_required
def toggle_subcribe_to_event(current_user, event_id):
    event = Event.query.filter_by(id=event_id).first()

    if not event:
        return jsonify({'message' : 'No event found'})

    operation = ""

    if current_user.attending_events.filter(str(event.id)).first():
        current_user.attending_events.remove(event)
        operation = "Succcessfully unsubscribed."
    else:
        current_user.attending_events.append(event)
        operation = "Succcessfully subscribed."

    db.session.commit()

    return jsonify({"message" : operation })


@app.route('/event/<event_id>', methods=['DELETE'])
@token_required
def delete_event(current_user, event_id):
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first()

    if not event:
        return jsonify({'message' : 'You are not authorised to delete this event, or this event does not exist.'})

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message' : 'Event deleted.'})

if __name__ == '__main__':
        app.run(debug=True,host='0.0.0.0')
