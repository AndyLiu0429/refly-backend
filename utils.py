from functools import wraps
from flask import g, request, redirect, url_for, jsonify
import config
from models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.verify_auth_token(request.json['token']) if 'token' in request.json else None
        if user is None:
            return jsonify({'message' : "authentication failed!"}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated_function