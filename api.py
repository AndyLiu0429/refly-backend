from app import app, db, bcrypt
from models import User, Group, Video
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

    if not data or 'user_fb_id' not in data or 'user_fb_name' not in data:
        return jsonify({'error' : 'Not valid paramaters'}), 400

    user = User.query.filter_by(user_fb_id = data['user_fb_id']).first()

    if user:
        return jsonify({"result" : "success"}), 200

    user = User(
      user_fb_id= data['user_fb_id'],
      user_fb_name= data['user_fb_name'],
    )

    try:
        db.session.add(user)
        db.session.commit()
        status = 'success'
        code = 200
    except:
        status = 'Service down'
        code = 500

    finally:
        db.session.close()

    return jsonify({'result' : status}), code

@app.route('/api/login', methods = ['POST'])
def login():
    data = request.json

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error' : 'Not valid paramaters'}), 400

    user = User.query.filter_by(username = data['username']).first()
    if user and bcrypt.check_password_hash(
        user.password, data['password']):
        token = user.generate_auth_token()
        code = 200
    else:
        return jsonify({'error' : 'wrong params'}), 404

    return jsonify({'token' : token}), code

@app.route('/api/logout', methods = ['POST'])
def logout():

    return jsonify({'result' : 'success'})

@app.route('/api/groups', methods = ['POST'])
#@login_required
def create_group():
    data = request.json

    if not data or 'user_fb_id' not in data or 'group_name' not in data:
        return jsonify({'error' : 'Not valid paramaters'}), 400

    user = User.query.filter_by(user_fb_id = data['user_fb_id']).first()
    if not user:
        return jsonify({'error' : 'Not valid paramaters'}), 400

    group = Group(
        name = data['group_name'],
        description="For test",
    )

    group.users.append(user)
    group_id = -1

    try:
        db.session.add(group)
        db.session.commit()
        group_id = group.id
        status = 'success'
        code = 200
    except:
        status = 'Service down'
        code = 500

    finally:
        db.session.close()

    return jsonify({'result' : status, 'group_id' : group_id}), code


@app.route('/api/groups', methods = ['GET'])
#@login_required
def get_groups():
    data = request.json
    groups = []

    if data and 'user_fb_id' in data:
        user = User.query.filter_by(user_fb_id = data['user_fb_id']).first()

        if user:
            groups = [group.id for group in user.groups]
    else:
        groups = [group.id for group in Group.query.all()]

    return jsonify({"group_ids" : groups}), 200

@app.route('/api/group/<int:group_id>/add', methods = ['POST'])
def add_group_member(group_id):
    data = request.json

    if not data or not 'user_fb_id':
        return jsonify({"error" : "Not valid parameters"}), 400

    group = Group.query.get(group_id)
    user = User.query.filter_by(user_fb_id = data['user_fb_id']).first()

    if not group or not user:
        return jsonify({"error" : "group not exists"}), 400

    group.users.append(user)
    user.groups.append(group)

    try:
        db.session.add(user)
        db.session.add(group)
        db.session.commit()
        status, code = "success", 200
    except:
        status, code = "Service down", 500

    finally:
        db.session.close()

    return jsonify({"result" : status}), code

@app.route('/api/group/<int:group_id>/members', methods = ['GET'])
def get_group_members(group_id):

    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error" : "group not exists"}), 400

    res = [{
        'user_fb_id' : user.user_fb_id,
        'user_fb_name' : user.user_fb_name
    }  for user in group.users]

    return jsonify({"result" : res}), 200

@app.route('/api/group/<int:group_id>', methods = ['GET'])
#@login_required
def get_group(group_id):
    data = request.json

    group = Group.query.get(group_id)

    return jsonify({
        'group_id' : group.id,
        'user_ids' : [user.id for user in group.users],
        'video_ids' : [video.id for video in group.videos],
        'group_name' : group.name,
        'group_desc' : group.description,
        'group_create_time' : group.created_at
    }), 200

@app.route('/api/group/<int:group_id>', methods = ['DELETE'])
#@login_required
def delete_group(group_id):
    data = request.json

    group = Group.query.get(group_id)

    try:
        db.session.delete(group)
        db.commit()
        status, code = "success", 200
    except:
        status, code = "Service down", 500
    finally:
        db.session.close()

    return jsonify({"result" : status}), code

@app.route('/api/group/<int:group_id>', methods = ['PUT'])
#@login_required
def update_group():
    pass


@app.route('/api/videos', methods = ['POST'])
def create_video():
    data = request.json

    if not data or not 'user_fb_id' in data or not 'video_s3_path' in data or \
            not 'group_ids' in data or not 'created_at' in data or not 'order' in data:
        pass

    video = Video.query.filter_by(video_s3_path = data['video_s3_path']).first()

    if video:
        return jsonify({"result" : "success"}), 200

    video = Video(
        video_s3_path=data['video_s3_path'],
        user_fb_id=data['user_fb_id'],
        created_at=data['created_at'],
        order = data['order']
    )

    for group_id in data['group_ids']:
        group = Group.query.get(group_id)
        if group:
            video.groups.append(group)

    # try:
    db.session.add(video)
    db.session.commit()
    status, code = "success", 200
    video_id = video.id
    # except:
    #      status, code = "service down", 500
    # finally:
    db.session.close()

    return jsonify({"result" : status, 'video_id' : video_id}), code

@app.route('/api/group/<int:group_id>/videos', methods=['GET'])
def get_group_videos(group_id):
    # data = request.json
    #
    # if not data:
    #     return jsonify({"error": "Not valid parameters" }), 400

    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Not valid parameters" }), 400

    res = []
    for video in group.videos:
        res.append({
            'video_id': video.id,
            'video_s3_path': video.video_s3_path,
            'user_fb_id' : video.user_fb_id,
            'created_at' : video.created_at,
            'order' : video.order
        })

    return jsonify({'result' : res}), 200


@app.route('/api/user/<user_fb_id>/groups', methods = ['GET'])
def get_user_groups(user_fb_id):

    user = User.query.filter_by(user_fb_id=user_fb_id).first()

    if not user :
        return jsonify({"error" : "wrong user_fb_id"}), 400

    res = [{
        'group_id' : group.id,
        'group_name' : group.name,
        'created_at' : group.created_at,
        'description' : group.description
    } for group in user.groups]

    return jsonify({"result" : res}), 200

@app.route('/api/user/<user_fb_id>/videos', methods=['GET'])
def get_user_videos(user_fb_id):

    user = User.query.filter_by(user_fb_id=user_fb_id).first()

    if not user:
        return jsonify({"error" : "wrong user_fb_id"}), 400

    res = [
        {
            'video_id': video.id,
            'video_s3_path': video.video_s3_path,
            'user_fb_id' : video.user_fb_id,
            'created_at' : video.created_at,
            'order' : video.order
        } for video in user.videos]

    return jsonify({"result" : res}), 200
