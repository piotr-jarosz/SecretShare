import datetime as dt
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
# from app import app
import json
import redis

r = redis.Redis()


class Secret:
    SALT = 'app.secret_keyas'
    bSALT = bytes(SALT, 'UTF-8')

    def __init__(self, secret_value: str, ttl, passphrase: str = ''):
        self.ittl = int(ttl)
        ### COMMENTED OUT DUE TO KRYPTOGRAPHY WORK NEEDED
        ### AES IS NOT BEST OPTION.
        # key = self.bSALT + bytes(passphrase, 'UTF-8') if passphrase else self.bSALT
        # iv = Random.new().read(AES.block_size)
        # cipher = AES.new(key, AES.MODE_CFB, iv)
        # secret = iv + cipher.encrypt(bytes(secret_value, 'UTF-8'))
        self.secret = secret_value  # secret.hex()
        self.created_at = dt.datetime.utcnow()
        self.end_of_life = self.created_at + dt.timedelta(hours=self.ittl)
        sid = secret_value + str(self.created_at) + self.SALT
        sid = sid.encode()
        self.secret_id = md5(sid).hexdigest()

    def save(self):
        secret = {self.secret_id: json.dumps({
            'secret': self.secret,
            'created_at': str(self.created_at),
            'end_of_life': str(self.end_of_life),
            'ttl': self.ittl
        })}
        secret_json = json.dumps(secret)
        r.mset(secret)
        return self.secret_id

    def destroy(secret_id: str):
        r.delete(secret_id)

    def read(secret_id: str, passphrase: str = ''):
        # key = self.bSALT + bytes(passphrase, 'UTF-8') if passphrase else self.bSALT
        # iv = Random.new().read(AES.block_size)
        # cipher = AES.new(key, AES.MODE_CFB, iv)
        # secret_value = cipher.decrypt(bytes.fromhex(secret))[len(iv):]
        secret = r.get(secret_id)
        if secret:
            secret = json.loads(secret)
        else:
            return None
        if dt.datetime.utcnow() < dt.datetime.strptime(secret['end_of_life'], '%Y-%m-%d %H:%M:%S.%f'):
            return secret
        else:
            Secret.destroy(secret_id)
            return False

    def __repr__(self):
        return '<Secret_id:{}>'.format(self.secret_id)
