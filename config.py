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
    ### REDIS CONFIG
    REDIS_HOST = environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(environ.get('REDIS_PORT')) if environ.get('REDIS_PORT') else 6379
    REDIS_PASSWORD = environ.get('REDIS_PASSWORD') or None
    REDIS_HEALTHCHECK = environ.get('REDIS_HEALTHCHECK') or 5
    REDIS_DB_ID = int(environ.get('REDIS_DB_ID')) if environ.get('REDIS_DB_ID') else 0
    REDIS_JQ_ID = int(environ.get('REDIS_JQ_ID')) if environ.get('REDIS_JQ_ID') else 1
    ### LOGS CONFIG
    LOG_PATH = environ.get('LOGS_PATH') or 'logs'
    LOG_LEVEL = environ.get('LOGS_LEVEL') or 'info'
    ### MAIL CONFIG
    EMAIL_SENDER = environ.get('EMAIL_SENDER') or 'no-reply@localhost'
    MAIL_SERVER = environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(environ.get('MAIL_PORT') or 1025)
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    ### USER MANAGEMENT
    REGISTRATION_DISABLED = environ.get('REGISTRATION_DISABLED') or False
    LOGIN_DISABLED = environ.get('REGISTRATION_DISABLED') or False
    ### RECAPTCHA CONFIG
    RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY') or None
    RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY') or None
    ### DB CONFIG
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Static config
    RECAPTCHA_PARAMETERS = {'render': 'explicit'}
    RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
    LANGUAGES = ['en',] # 'pl']

    # conditional config

    ## when no db configured set LOGIN AND REGISTRATION TO DISABLED
    if environ.get('SQLALCHEMY_DATABASE_URI') is None and not environ.get('FLASK_DEBUG'):
        REGISTRATION_DISABLED = True
        LOGIN_DISABLED = True