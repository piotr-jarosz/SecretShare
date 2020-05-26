from flask import Flask, current_app, request
from config import Config
from flask_bootstrap import Bootstrap
from redis import Redis
from fakeredis import FakeStrictRedis
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
c = Config()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
mail = Mail()



def create_app(config_class=c):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    mail.init_app(app)
    if app.testing:
        app.redis = FakeStrictRedis()
        app.logger.info('Mocking redis')
    else:
        app.redis = Redis(host=c.REDIS_HOST,
                          port=c.REDIS_PORT,
                          password=c.REDIS_PASSWORD,
                          health_check_interval=c.REDIS_HEALTHCHECK,
                          db=c.REDIS_DB_ID)
    moment.init_app(app)
    babel.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.secret import bp as secret_bp
    app.register_blueprint(secret_bp)

    from app.manager import bp as manager_bp
    app.register_blueprint(manager_bp, url_prefix='/manager')

    if not app.debug and not app.testing:
        log_path = app.config['LOG_PATH']
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        file_handler = RotatingFileHandler(log_path + '/app.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s]: %(message)s [in %(pathname)s:%(lineno)d]'))
        if app.config['LOG_LEVEL'] == 'DEBUG':
            file_handler.setLevel(logging.DEBUG)
        if app.config['LOG_LEVEL'] == 'INFO':
            file_handler.setLevel(logging.INFO)
        if app.config['LOG_LEVEL'] == 'WARN':
            file_handler.setLevel(logging.WARN)
        if app.config['LOG_LEVEL'] == 'ERROR':
            file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        app.logger.info('Application start')
        app.logger.info('db: ' + str(db))

    app.logger.setLevel(logging.INFO)

    @app.context_processor
    def is_login():
        return dict(login_disabled=app.config['LOGIN_DISABLED'])

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

from app import models
