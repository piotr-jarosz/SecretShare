from flask import render_template, current_app
from flask_babel import _
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_password_token()
    send_email(_('[SecretShare] Reset Your Password'),
               sender=current_app.config['EMAIL_SENDER'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_account_activation_token(user):
    token = user.get_password_token()
    send_email(_('[SecretShare] Activate account!'),
               sender=current_app.config['EMAIL_SENDER'],
               recipients=[user.email],
               text_body=render_template('email/activate_account.txt',
                                         user=user, token=token),
               html_body=render_template('email/activate_account.html',
                                         user=user, token=token))