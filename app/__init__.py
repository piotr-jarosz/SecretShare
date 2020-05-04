from flask import Flask, current_app, request
from config import Config
from flask_bootstrap import Bootstrap
from redis import Redis
from fakeredis import FakeStrictRedis
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_moment import Moment
from flask_babel import Babel

c = Config()
b = Bootstrap()
m = Moment()
babel = Babel()



def create_app(config_class=c):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)
    b.init_app(app)
    if app.testing:
        app.redis = FakeStrictRedis()
        app.logger.info('Mocking redis')
    else:
        app.redis = Redis(host=c.REDIS_HOST, port=c.REDIS_PORT, password=c.REDIS_PASSWORD, health_check_interval=c.REDIS_HEALTHCHECK)
    m.init_app(app)
    babel.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.secret import bp as secret_bp
    app.register_blueprint(secret_bp, url_prefix='/secret')

    if not app.debug:
        lp = app.config['LOGS_PATH']
        if not os.path.exists(lp):
            os.mkdir(lp)
        file_handler = RotatingFileHandler(lp + '/app.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s]: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Application start')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
