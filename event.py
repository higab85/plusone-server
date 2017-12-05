from main import app, token_required, db
from flask import jsonify, request
import uuid
from models import Event


@app.route('/event', methods=['GET'])
@token_required
def get_all_events(current_user):
    events = Event.query.filter(Event.user_id==current_user.id)

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
    event_data['subscribed'] =  event in set(current_user.attending_events.all())

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
