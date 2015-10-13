from app import app, db
from models import User
from flask import Flask, request, jsonify, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt

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

    user = User.query.filter_by(email = data['email']).first()
    if user and bcrypt.check_password_hash(
        user.password, data['password']):
        session['logged_in'] = True
        status = True
        code = 200
    else:
        status = False
        code = 404

    return jsonify({'result' : status}), code

@app.route('/api/logout', methods = ['POST'])
def logout():
    session.pop('logged_in', None)
    return jsonify({'result' : 'success'})