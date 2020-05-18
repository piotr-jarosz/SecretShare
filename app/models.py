import datetime as dt
from hashlib import md5
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from random import randint
from base64 import urlsafe_b64encode
from config import Config as C
import json


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
            sid = str(self.created_at) + ''.join([str(randint(0, 10)) for _ in range(10)])
            sid = sid.encode()
            self.obj_id = md5(sid).hexdigest()

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
        obj_id = md5(secret_id.encode()).hexdigest()
        ttl = secret.ttl
        return Admin(secret_id=secret_id, obj_id=obj_id, ttl=ttl)
