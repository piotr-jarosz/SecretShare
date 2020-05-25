from json import loads
import unittest
from flask import url_for
from app import create_app, db
from config import Config
from app.models import Secret, Admin, User
from app.redis_registry import RedisRegistry


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = False


class BasicTests(unittest.TestCase):

    # decorator function to log succeeded tests
    def _logger(func):
        def decorator(self):
            func(self)
            self.app.logger.info(func.__name__ + ' DONE')
        return decorator

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.app_client = self.app.test_client()

    # executed after each test
    def tearDown(self):
        self.app_context.pop()

    ######################################
    ####          unit tests          ####
    ######################################

    # TBD

    ######################################
    #### functional/integration tests ####
    ######################################

    @_logger
    def test_main_page(self):
        response = self.app_client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @_logger
    def test_create_secret_with_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
            'passphrase': 'empty'
        }
        keys_count = len(self.app.redis.keys())
        response = self.app_client.post(url_for('secret.index'), follow_redirects=True, data=data)
        self.assertEqual(keys_count + 2, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)

    @_logger
    def test_create_secret_without_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1'
        }
        keys_count = len(self.app.redis.keys())
        response = self.app_client.post(url_for('secret.index'), follow_redirects=True, data=data)
        self.assertEqual(keys_count + 2, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)

    @_logger
    def test_read_secret_with_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
            'passphrase': 'empty'
        }
        s = Secret(secret_value=data['secret'], ttl=int(data['ttl']), passphrase=data['passphrase'])
        RedisRegistry(s).save()
        secret_id = s.obj_id
        keys_count = len(self.app.redis.keys())
        response = self.app_client.get(url_for('secret.read_secret', secret_id=secret_id), follow_redirects=True)
        self.assertEqual(keys_count, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)
        response = self.app_client.post(url_for('secret.read_secret',
                                                secret_id=secret_id),
                                        data=data)
        self.assertEqual(keys_count - 1, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.get_data(as_text=True))['secret'], data['secret'])

    @_logger
    def test_read_secret_without_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
        }
        s = Secret(secret_value=data['secret'], ttl=int(data['ttl']))
        RedisRegistry(s).save()
        secret_id = s.obj_id
        keys_count = len(self.app.redis.keys())
        response = self.app_client.get(url_for('secret.read_secret', secret_id=secret_id), follow_redirects=True)
        self.assertEqual(keys_count, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)
        response = self.app_client.post(url_for('secret.read_secret',
                                                secret_id=secret_id),
                                        data=data)
        self.assertEqual(keys_count - 1, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(loads(response.get_data(as_text=True))['secret'], data['secret'])


    @_logger
    def test_delete_secret_with_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
            'passphrase': 'Test',
        }
        s = Secret(secret_value=data['secret'], ttl=int(data['ttl']), passphrase=data['passphrase'])
        a = Admin.create_admin(s)
        RedisRegistry(s).save()
        RedisRegistry(a).save()
        keys_count = len(self.app.redis.keys())
        response = self.app_client.post(url_for('secret.secret_admin', admin_id=a.obj_id), follow_redirects=True,
                                        data={'submit': 'Burn the Secret!', })
        self.assertEqual(keys_count - 1, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)
        response = self.app_client.get(url_for('secret.secret_admin', admin_id=a.obj_id))
        self.assertNotEqual(response.status_code, 200)

    @_logger
    def test_admin_page(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
        }
        s = Secret(secret_value=data['secret'], ttl=int(data['ttl']))
        a = Admin.create_admin(s)
        RedisRegistry(s).save()
        RedisRegistry(a).save()
        admin_id = a.obj_id
        keys_count = len(self.app.redis.keys())
        response = self.app_client.get(url_for('secret.secret_admin', admin_id=admin_id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys_count, len(self.app.redis.keys()))


    @_logger
    def test_admin_page__secret_doesnt_exist(self):
        response = self.app_client.get(url_for('secret.secret_admin', admin_id='non'), follow_redirects=True)
        self.assertEqual(response.status_code, 404)

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
