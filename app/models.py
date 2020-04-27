import datetime as dt
from hashlib import md5
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from random import randint
from base64 import urlsafe_b64encode
from flask import current_app
import json


class Secret:

    def __init__(self, secret_value: str, ttl: int, passphrase='', created_at: str = str(dt.datetime.utcnow()),
                 encrypted=False, secret_id: str = ''):
        self.ttl = int(ttl)
        self.passphrase = True if passphrase else False
        if not encrypted:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=bytes(current_app.config['SECRET_KEY'], 'UTF-8'), iterations=100000,
                             backend=default_backend())
            bpassphrase = bytes(passphrase, 'UTF-8')
            key = urlsafe_b64encode(kdf.derive(bpassphrase))
            f = Fernet(key)
            encrypted = f.encrypt(bytes(secret_value, 'UTF-8'))
            self.secret = encrypted
        else:
            self.secret = secret_value
        self.created_at = dt.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
        self.end_of_life = self.created_at + dt.timedelta(hours=self.ttl)
        sid = str(self.created_at) + ''.join([str(randint(0, 10)) for _ in range(10)])
        sid = sid.encode()
        self.secret_id = secret_id if secret_id else md5(sid).hexdigest()

    def save(self):
        secret = {self.secret_id: json.dumps({
            'secret': str(self.secret),
            'created_at': str(self.created_at),
            'passphrase': self.passphrase,
            'ttl': self.ttl
        })}
        current_app.redis.mset(secret)
        current_app.redis.expire(self.secret_id, dt.timedelta(hours=self.ttl))
        return self.secret_id

    def destroy(self):
        current_app.redis.delete(self.secret_id)

    def load(secret_id: str):
        secret = current_app.redis.get(secret_id)
        if secret:
            secret = json.loads(secret)
            return Secret(secret['secret'], ttl=int(secret['ttl']), created_at=secret['created_at'], encrypted=True,
                          secret_id=secret_id, passphrase=secret['passphrase'])
        else:
            return False

    def read(self, passphrase: str = ''):
        if dt.datetime.utcnow() < self.end_of_life:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=bytes(current_app.config['SECRET_KEY'], 'UTF-8'), iterations=100000,
                             backend=default_backend())
            bpassphrase = bytes(passphrase, 'UTF-8')
            key = urlsafe_b64encode(kdf.derive(bpassphrase))
            f = Fernet(key)
            try:
                decrypted = f.decrypt(eval(self.secret)).decode()
            except InvalidToken:
                return False
            Secret.destroy(self)
            return decrypted
        else:
            Secret.destroy(self)
            return False

    def __repr__(self):
        return json.dumps({self.secret_id: {
            'secret': str(self.secret),
            'created_at': str(self.created_at),
            'ttl': self.ttl,
            'passphrase': self.passphrase
        }})
