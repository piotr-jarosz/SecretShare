from json import loads
import os
import unittest
from datetime import datetime, timedelta
from flask import url_for
from app import create_app
from app import current_app
from config import Config
from app.models import Secret
import traceback


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
        # self.logger()

    @_logger
    def test_create_secret_with_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
            'passphrase': 'empty'
        }
        keys_count = len(self.app.redis.keys())
        response = self.app_client.post('/secret', follow_redirects=True, data=data)
        self.assertEqual(keys_count + 1, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)

    @_logger
    def test_create_secret_without_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1'
        }
        keys_count = len(self.app.redis.keys())
        response = self.app_client.post('/secret', follow_redirects=True, data=data)
        self.assertEqual(keys_count + 1, len(self.app.redis.keys()))
        self.assertEqual(response.status_code, 200)

    @_logger
    def test_read_secret_with_passphrase(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
            'passphrase': 'empty'
        }
        s = Secret(secret_value=data['secret'], ttl=int(data['ttl']), passphrase=data['passphrase'])
        secret_id = s.save()
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
        secret_id = s.save()
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


## COMMENTED OUT DUE TO ERRORS WITH POSTING FORM
    #TODO: fix this test:

    # @_logger
    # def test_delete_secret_with_passphrase(self):
    #     data = {
    #         'secret': 'TestSecret',
    #         'ttl': '1',
    #         'passphrase': 'Test',
    #     }
    #     s = Secret(secret_value=data['secret'], ttl=int(data['ttl']), passphrase=data['passphrase'])
    #     secret_id = s.save()
    #     keys_count = len(self.app.redis.keys())
    #     response = self.app_client.post(url_for('secret.secret_admin', secret_id=secret_id), follow_redirects=True,
    #                                     data={'burn_form': '', },
    #                                     headers={"Content-Type": "application/x-www-form-urlencoded"})
    #     self.assertEqual(keys_count - 1, len(self.app.redis.keys()))
    #     self.assertEqual(response.status_code, 200)
    #     response = self.app_client.post(url_for('secret.secret_admin', secret_id=secret_id), data=data)
    #     self.assertNotEqual(response.status_code, 200)

    @_logger
    def test_admin_page(self):
        data = {
            'secret': 'TestSecret',
            'ttl': '1',
        }
        s = Secret(secret_value=data['secret'], ttl=int(data['ttl']))
        secret_id = s.save()
        keys_count = len(self.app.redis.keys())
        response = self.app_client.get(url_for('secret.secret_admin', secret_id=secret_id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys_count, len(self.app.redis.keys()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
