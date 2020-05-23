from flask import render_template, current_app
from flask_babel import _
from app.email import send_email
from app.models import Secret


def send_secret_link_email(secret: Secret, recivers: list):
    send_email(_('[SecretShare] Your SecretLink'),
               sender=current_app.config['EMAIL_SENDER'],
               recipients=recivers,
               text_body=render_template('email/send_secret_link.txt',
                                         secret=secret),
               html_body=render_template('email/send_secret_link.html',
                                         secret=secret)
               )
