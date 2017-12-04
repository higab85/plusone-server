# https://www.youtube.com/watch?v=WxGBoY5iNXY
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


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

from event import *
from user import *
from chat import *



if __name__ == '__main__':
     app.debug = True
     app.run(host='0.0.0.0', port=5000, threaded=True)
    # app.run(debug=True,host='0.0.0.0')

    # NOTE: only for testing, in production use above line and comment the
    # one below
    #app.run(debug=True, threaded=True)
