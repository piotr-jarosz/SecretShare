from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

if not app.debug:
    lp = Config.LOGS_PATH
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

from app import routes, errors
