from main import app, token_required, db
from flask import jsonify, make_response, request
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from models import User

def jsonifyEvents(events, user):
    output = []
    for event in events:
        event_data = get_event_data(event, user)
        output.append(event_data)
    return jsonify(output)

def get_event_data(event, user):
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
    event_data['subscription'] =  event in set(user.attending_events.all())
    return event_data

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
@app.route('/user/<email>', methods=['GET'])
@token_required
def get_one_user(current_user, email):
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message':'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['email'] = user.email

    return jsonify(user_data)

@app.route('/user/<email>/events', methods=['GET'])
@token_required
def get_event_subscriptions_from(current_user, email):
    print("email: " + email)
    user = User.query.filter_by(email=email).first()
    events = user.attending_events
    return jsonifyEvents(events, current_user)


# TODO: Handle error when email already exists
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New user created!'})

@app.route('/user', methods=['PUT'])
@token_required
def modify_user(current_user):
    data = request.get_json()
    current_user.name = data['name']
    current_user.email = data['email']
    current_user.password = generate_password_hash(data['password'], method='sha256')
    db.session.commit()
    return jsonify({'message':'User modified!'})

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

        return  token.decode('UTF-8')

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
