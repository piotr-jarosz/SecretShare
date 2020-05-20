import datetime as dt
import uuid
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from base64 import urlsafe_b64encode
from config import Config as C
import json
from app import db, login
from flask_login import UserMixin
from time import time


class Secret:

    def __init__(self, *initial_data, passphrase: str = '', **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.ttl = int(self.ttl)
        if passphrase:
            self.passphrase = True
        elif hasattr(self, 'passphrase') and self.passphrase:
            passphrase = self.passphrase
            self.passphrase = True
        else:
            self.passphrase = False
            passphrase: str = ''
        self.encrypted = self.encrypted if hasattr(self, 'encrypted') else False
        self.from_db = self.from_db if hasattr(self, 'from_db') else False
        if not self.from_db and not self.encrypted:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                             salt=bytes(C.SECRET_KEY, 'UTF-8'), iterations=100000,
                             backend=default_backend())
            bpassphrase = bytes(passphrase, 'UTF-8')
            key = urlsafe_b64encode(kdf.derive(bpassphrase))
            f = Fernet(key)
            encrypted = f.encrypt(bytes(self.secret_value, 'UTF-8'))
            self.secret = encrypted
        if hasattr(self, 'created_at'):
            self.created_at = dt.datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S.%f')
        else:
            self.created_at = dt.datetime.utcnow()
        self.end_of_life = self.created_at + dt.timedelta(hours=self.ttl)
        if not hasattr(self, 'obj_id'):
            self.obj_id = str(uuid.uuid4())

    def __dict__(self):
        secret = {self.obj_id: {
            'secret': str(self.secret),
            'created_at': str(self.created_at),
            'passphrase': self.passphrase,
            'ttl': self.ttl
        }}
        return secret

    def read(self, passphrase: str = ''):
        if dt.datetime.utcnow() < self.end_of_life:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                             salt=bytes(C.SECRET_KEY, 'UTF-8'),
                             iterations=100000,
                             backend=default_backend())
            bpassphrase = bytes(passphrase, 'UTF-8')
            key = urlsafe_b64encode(kdf.derive(bpassphrase))
            f = Fernet(key)
            try:
                decrypted = f.decrypt(eval(self.secret)).decode()
            except InvalidToken:
                return False
            return decrypted
        else:
            return False

    def __repr__(self):
        return json.dumps({self.obj_id: {
            'secret': str(self.secret),
            'created_at': str(self.created_at),
            'ttl': self.ttl,
            'passphrase': self.passphrase
        }})


class Admin:

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __dict__(self):
        admin = {self.obj_id: {
            'secret_id': str(self.secret_id)
        }}
        return admin

    @classmethod
    def create_admin(cls, secret: Secret):
        secret_id = secret.obj_id
        obj_id = str(uuid.uuid4())
        ttl = secret.ttl
        return Admin(secret_id=secret_id, obj_id=obj_id, ttl=ttl)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    secrets = db.relationship('AdminManager', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def activate_account(self, activation: bool=True):
        self.password_hash = activation

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def get_password_token(self, expires_in=600):
        return jwt.encode(
            {'set_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_set_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['set_password']
        except:
            return
        return User.query.get(id)


class AdminManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(140), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=dt.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<AdminManager {}>'.format(self.body)