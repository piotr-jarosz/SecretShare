from flask import Flask, current_app
from config import Config
from flask_bootstrap import Bootstrap
from redis import Redis
import logging
from logging.handlers import RotatingFileHandler
import os

c = Config()
b = Bootstrap()
r = Redis(host=c.REDIS_HOST, port=c.REDIS_PORT, password=c.REDIS_PASSWORD)

def create_app(config_class=c):
    app = Flask(__name__)
    app.config.from_object(config_class)
    b.init_app(app)
    app.redis = r

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


from app import models
