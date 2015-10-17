from app import app, db, bcrypt
from models import User
from flask import Flask, request, jsonify, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from utils import login_required


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/api/register', methods = ['POST'])
def register():

    data = request.json

    if 'email' not in data or 'username' not in data or 'password' not in data:
        return jsonify({'result' : 'Not valid paramaters'}), 400

    user = User(
        email = data['email'],
        username = data['username'],
        password = data['password']
    )
    try:
        db.session.add(user)
        db.session.commit()
        status = 'success'
        code = 200
    except:
        status = 'User is already registered'
        code = 409
    finally:
        db.session.close()

    return jsonify({'result' : status}), code

@app.route('/api/login', methods = ['POST'])
def login():
    data = request.json

    if 'username' not in data or 'password' not in data:
        return jsonify({'result' : 'Not valid paramaters'}), 400

    user = User.query.filter_by(username = data['username']).first()
    if user and bcrypt.check_password_hash(
        user.password, data['password']):
        token = user.generate_auth_token()
        code = 200
    else:
        token = 'bad'
        code = 404

    return jsonify({'token' : token}), code

@app.route('/api/logout', methods = ['POST'])
def logout():

    return jsonify({'result' : 'success'})

@app.route('/api/group', methods = ['POST'])
@login_required
def create_group():
    return "haah"

@app.route('/api/group', methods = ['GET'])
@login_required
def get_groups():
    pass

@app.route('/api/group/<int:group_id>', methods = ['GET'])
@login_required
def get_group():
    pass

@app.route('/api/group/<int:group_id>', methods = ['DELETE'])
@login_required
def delete_group():
    pass

@app.route('/api/group/<int:group_id>', methods = ['PUT'])
@login_required
def update_group():
    pass



