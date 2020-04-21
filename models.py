import datetime as dt
from hashlib import md5
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import Config
import random
import base64
import json
import redis

r = redis.Redis()
c = Config()


class Secret:
    SALT = c.SECRET_KEY
    bSALT = bytes(SALT, 'UTF-8')

    def __init__(self, secret_value: str, ttl, passphrase = '', created_at: str = str(dt.datetime.utcnow()),
                 encrypted = False, secret_id: str = ''):
        self.ittl = int(ttl)
        self.passphrase = True if passphrase else False
        if not encrypted:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.bSALT, iterations=100000,
                             backend=default_backend())
            bpassphrase = bytes(passphrase, 'UTF-8')
            key = base64.urlsafe_b64encode(kdf.derive(bpassphrase))
            f = Fernet(key)
            encrypted = f.encrypt(bytes(secret_value, 'UTF-8'))
            self.secret = encrypted
        else:
            self.secret = secret_value
        self.created_at = dt.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
        self.end_of_life = self.created_at + dt.timedelta(hours=self.ittl)
        sid = str(self.created_at) + ''.join([str(random.randint(0,10)) for _ in range(10)])
        sid = sid.encode()
        self.secret_id = secret_id if secret_id else md5(sid).hexdigest()

    def save(self):
        secret = {self.secret_id: json.dumps({
            'secret': str(self.secret),
            'created_at': str(self.created_at),
            'end_of_life': str(self.end_of_life),
            'passphrase': self.passphrase,
            'ttl': self.ittl
        })}
        r.mset(secret)
        return self.secret_id

    def destroy(self):
        r.delete(self.secret_id)

    def load(secret_id: str):
        secret = r.get(secret_id)
        if secret:
            secret = json.loads(secret)
            return Secret(secret['secret'], ttl=secret['ttl'], created_at=secret['created_at'], encrypted=True,
                      secret_id=secret_id, passphrase=secret['passphrase'])
        else:
            return False

    def read(self, passphrase: str = ''):
        if dt.datetime.utcnow() < self.created_at + dt.timedelta(hours=self.ittl):
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self.bSALT, iterations=100000,
                             backend=default_backend())
            bpassphrase = bytes(passphrase, 'UTF-8')
            key = base64.urlsafe_b64encode(kdf.derive(bpassphrase))
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
            'end_of_life': str(self.end_of_life),
            'ttl': self.ittl,
            'passphrase': self.passphrase
        }})
