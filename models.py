import datetime
from app import db, bcrypt
import config
from sqlalchemy.dialects.postgresql import JSON
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

user_group = db.Table('user_group',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
                      db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key = True))


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable = False)
    created_at = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    videos = db.relationship('Video', backref = 'user')
    groups = db.relationship('Group', secondary = user_group)

    def generate_auth_token(self, expiration = 1400):
        s = Serializer(config.SECRET_KEY, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    def __init__(self, email, password, username, admin=False):
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.created_at = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {0}>'.format(self.username)

class Group(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False)
    videos = db.relationship('Video', backref = 'group')
    users = db.relationship('User', secondary = user_group)

    def __init__(self, name, description):
        self.created_at = datetime.datetime.now()
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Group {0}>'.format(self.name)

class Video(db.Model):

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    video_id = db.Column(db.String(50)) # s3 unique id
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable = False)
    order = db.Column(db.Integer)

    def __init__(self, video_id, group, user, created_at, order):
        self.video_id = video_id
        self.group = group
        self.user = user
        self.created_at = created_at
        self.order = order

    def __repr__(self):
        return '<Video {0}>'.format(self.video_id)




