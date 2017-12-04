from main import db

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
