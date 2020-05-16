import json
from flask import render_template, flash as flask_flash, redirect, url_for, request, current_app, abort, g
from redis import ConnectionError
from flask_babel import _, get_locale
from requests import post

from app.models import Secret
from app.secret import bp
from app.secret.forms import SecretForm, ReadSecretForm, SendSecretLink, SendPassphrase
from app.email import send_secret_link_email


def flash(message): flask_flash(message, category='info')

def is_human(captcha_response):
    payload = {'response': captcha_response, 'secret': current_app.config['RECAPTCHA_PRIVATE_KEY']}
    response = post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    response_text = json.loads(response.text)
    return response_text

@bp.before_request
def before_request():
    g.locale = str(get_locale())


@bp.route("/", methods=['GET', 'POST'])
def index():
    form = SecretForm()
    if form.validate_on_submit():
        secret = Secret(form.secret.data, form.ttl.data, passphrase=form.passphrase.data)
        try:
            secret_id = secret.save()
        except ConnectionError as e:
            current_app.logger.error(e)
            return 500
        if secret_id:
            flash('Secret created!')
        return redirect(url_for('secret.secret_admin', secret_id=secret_id))
    return render_template('secrets/index.html', title=_('Create your secret now!'), form=form)


@bp.route("/<secret_id>/", methods=['GET', 'POST', 'DELETE'])
def read_secret(secret_id: str):
    s = Secret.load(secret_id)
    if request.method == 'DELETE':
        s.destroy()
        flash(_('Secret destroyed!'))
        return 'Ok'
    if s:
        passphrase = s.passphrase
        form = ReadSecretForm()
        if form.validate_on_submit():
            from html import escape
            secret = escape(s.read(passphrase=form.passphrase.data))
            if secret:
                return json.dumps({'secret': secret})
            else:
                return json.dumps({'secret': secret}), 404
    else:
        form = False
        passphrase = False
        abort(404)
    return render_template('secrets/secret.html', passphrase=passphrase, secret_id=secret_id, form=form)


@bp.route("/<secret_id>/admin/", methods=['GET', 'POST'])
def secret_admin(secret_id):
    secret = Secret.load(secret_id)
    sms_form = SendPassphrase()
    email_form = SendSecretLink()
    if sms_form.submit_sms.data and sms_form.validate():
        flash('SMS sent!')

    if email_form.submit_email.data and email_form.validate():
        flash('Email sent!')
        send_secret_link_email(recivers=[email_form.email.data], secret=secret)
    return render_template('secrets/secret_admin.html',
                           secret=secret,
                           secret_id=secret_id,
                           email_form=email_form,
                           sms_form=sms_form
                           )
