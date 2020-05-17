from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail
from app.models import Secret


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
        current_app.logger.info('Email sent')
    else:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()
        current_app.logger.info('Email sent')


def send_secret_link_email(secret: Secret, recivers: list):
    send_email('[SecretShare] Your SecretLink',
               sender=current_app.config['EMAIL_SENDER'],
               recipients=recivers,
               text_body=render_template('email/send_secret_link.txt',
                                         secret=secret),
               html_body=render_template('email/send_secret_link.html',
                                         secret=secret)
               )
