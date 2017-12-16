from main import app, token_required, db
from flask import jsonify, request
import uuid
from models import Event


def jsonifyEvents(events, current_user):
    output = []
    for event in events:
        event_data = get_event_data(event, current_user)
        output.append(event_data)
    return jsonify(output)

def get_event_data(event, current_user):
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
    event_data['subscription'] =  event in set(current_user.attending_events.all())
    return event_data

@app.route('/event', methods=['GET'])
@token_required
def get_events(current_user):
    args = request.args

    attributes = {
        'name':Event.name,
        'user_id':Event.user_id,
        'description':Event.description,
        'start':Event.start,
        'end':Event.end,
        'type':Event.type,
        'latitude': Event.latitude,
        'longitude': Event.longitude
    }

    events = Event.query
    for key in args:
        events = events.filter(attributes[key].contains(args[key]))

    return jsonifyEvents(events, current_user)



@app.route('/event/<event_id>', methods=['GET'])
@token_required
def get_one_event(current_user, event_id):
    event = Event.query.filter_by(id=event_id).first()

    if not event:
        return jsonify({'message' : 'No event found'})

    event_data = get_event_data(event, current_user)

    return jsonify(event_data)

@app.route('/event', methods=['POST'])
@token_required
def create_event(current_user):
    data = request.get_json()

    new_event = Event(
        public_id=str(uuid.uuid4()),
        user_id=current_user.public_id,
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
    event_id_str = str(event_id)
    event = Event.query.filter_by(id=event_id_str).first()

    if not event:
        return jsonify({'message' : 'No event found'})

    operation = ""

    if event in current_user.attending_events:
        current_user.attending_events.remove(event)
        operation = "Succcessfully unsubscribed."
    else:
        current_user.attending_events.append(event)
        operation = "Succcessfully subscribed."

    db.session.commit()

    return jsonify({"message" : operation })


@app.route('/event/<event_id>', methods=['DELETE'])
@token_required
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id).first()

    if not event:
        return jsonify({'message' : 'You are not authorised to delete this event, or this event does not exist.'})

    db.session.delete(event)
    db.session.commit()

    return jsonify({'message' : 'Event deleted.'})

@app.route('/event/<event_id>/users', methods=['GET'])
@token_required
def get_users_subscribed_to(current_user, event_id):
    event = Event.query.filter_by(id=event_id).first()
    users = event.attendees
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['email'] = user.email
        output.append(user_data)
    return jsonify(output)
