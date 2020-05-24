import json
from flask import render_template,redirect, url_for, request, current_app, abort, g
from app.helpers import flash
from redis import ConnectionError
from flask_babel import _, get_locale
from app import login, db
from app.models import Secret, Admin, User
from app.secret import bp
from app.secret.forms import SecretForm, ReadSecretForm, SendSecretLink, SendPassphrase, BurnSecretForm
from app.secret.email import send_secret_link_email
from app.redis_registry import RedisRegistry


# def is_human(captcha_response):
#     payload = {'response': captcha_response, 'secret': current_app.config['RECAPTCHA_PRIVATE_KEY']}
#     response = post("https://www.google.com/recaptcha/api/siteverify", data=payload)
#     response_text = json.loads(response.text)
#     return response_text


@bp.before_request
def before_request():
    g.locale = str(get_locale())


@bp.route("/", methods=['GET', 'POST'])
def index():
    form = SecretForm()
    if form.validate_on_submit():
        secret = Secret(secret_value=form.secret.data, ttl=form.ttl.data, passphrase=form.passphrase.data)
        try:
            RedisRegistry(secret).save()
            admin = Admin.create_admin(secret)
            RedisRegistry(admin).save()
        except ConnectionError as e:
            current_app.logger.error(e)
            return 500
        flash('Secret created!')
        return redirect(url_for('secret.secret_admin', admin_id=admin.obj_id))
    return render_template('secrets/index.html', title=_('Create your secret now!'), form=form)


@bp.route("/secret/<secret_id>/", methods=['GET', 'POST'])
def read_secret(secret_id: str):
    s = RedisRegistry.load(secret_id, Secret)
    if s:
        passphrase = True if s.passphrase else False
        current_app.logger.debug('Secret exists and passphrase state is: ' + str(passphrase))
    else:
        passphrase = True
        current_app.logger.debug('Secret doesnt exist')
    form = ReadSecretForm()
    if form.validate_on_submit():
        if not s:
            current_app.logger.debug('Form is valid but secret doesn\'t exist')
            return json.dumps({'secret': False}), 404
        from html import escape
        secret = s.read(passphrase=form.passphrase.data)
        current_app.logger.debug('Secret is: ' + str(secret))

        if secret:
            RedisRegistry(s).destroy()
            return json.dumps({'secret': escape(secret)})
        else:
            return json.dumps({'secret': False}), 404
    return render_template('secrets/secret.html', passphrase=passphrase, secret_id=secret_id, form=form)


@bp.route("/admin/<admin_id>/", methods=['GET', 'POST'])
def secret_admin(admin_id):
    admin = RedisRegistry.load(admin_id, Admin)
    secret = RedisRegistry.load(admin.secret_id, Secret) if admin else False
    if secret:
        sms_form = SendPassphrase()
        email_form = SendSecretLink()
        burn_form = BurnSecretForm()
        if sms_form.submit_sms.data and sms_form.validate():
            flash('SMS sent!')
        if email_form.submit_email.data and email_form.validate():
            flash('Email sent!')
            send_secret_link_email(recivers=[email_form.email.data], secret=secret)
        if burn_form.submit.data and burn_form.validate():
            if RedisRegistry(secret).destroy():
                current_app.logger.debug(request.form)
                flash('Secret destroyed!')
                return redirect(url_for('secret.index'))
        return render_template('secrets/secret_admin.html',
                               secret=secret,
                               secret_id=secret.obj_id,
                               admin_id=admin_id,
                               email_form=email_form,
                               sms_form=sms_form,
                               burn_form=burn_form
                               )
    abort(404)
