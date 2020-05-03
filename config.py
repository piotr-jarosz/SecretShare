from os import environ


class Config(object):
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    REDIS_HOST = environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(environ.get('REDIS_PORT')) if environ.get('REDIS_PORT') else 6379
    REDIS_PASSWORD = environ.get('REDIS_PASSWORD') or None
    REDIS_HEALTHCHECK = environ.get('REDIS_HEALTHCHECK') or 5
    LOGS_PATH = environ.get('LOGS_PATH') or 'logs'
