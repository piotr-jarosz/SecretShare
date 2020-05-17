from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    """
    Environment configuration Class
    """
    # ENV config
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    REDIS_HOST = environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(environ.get('REDIS_PORT')) if environ.get('REDIS_PORT') else 6379
    REDIS_PASSWORD = environ.get('REDIS_PASSWORD') or None
    REDIS_HEALTHCHECK = environ.get('REDIS_HEALTHCHECK') or 5
    LOGS_PATH = environ.get('LOGS_PATH') or 'logs'
    REDIS_DB_ID = int(environ.get('REDIS_DB_ID')) if environ.get('REDIS_DB_ID') else 0
    REDIS_JQ_ID = int(environ.get('REDIS_JQ_ID')) if environ.get('REDIS_JQ_ID') else 1
    EMAIL_SENDER = environ.get('EMAIL_SENDER') or 'no-reply@secret.icoqu.com'
    MAIL_SERVER = environ.get('MAIL_SERVER')
    MAIL_PORT = int(environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL  = environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY') or None
    RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY') or None

    # Static config
    RECAPTCHA_PARAMETERS = {'render': 'explicit'}
    RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
    LANGUAGES = ['en',] # 'pl']
