import json
from flask import render_template, flash as flask_flash, redirect, url_for, request, current_app, abort
from app.secret.forms import SecretForm, ReadSecretForm
from app.secret import bp
from app.models import Secret
from functools import partial
from redis import ConnectionError

flash = partial(flask_flash, category='info')


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
    return render_template('secrets/index.html', title='Create your secret now!', form=form)


@bp.route("/<secret_id>/", methods=['GET', 'POST', 'DELETE'])
def read_secret(secret_id: str):
    s = Secret.load(secret_id)
    if request.method == 'DELETE':
        s.destroy()
        return 'Ok'
    if s:
        passphrase = s.passphrase
        form = ReadSecretForm()
        if form.validate_on_submit():
            secret = s.read(passphrase=form.passphrase.data)
            if secret:
                return json.dumps({'secret': secret})
            else:
                return json.dumps({'secret': secret}), 404
    else:
        form = False
        passphrase = False
        abort(404)
    return render_template('secrets/secret.html', passphrase=passphrase, secret_id=secret_id, form=form)


@bp.route("/<secret_id>/admin/")
def secret_admin(secret_id):
    secret = Secret.load(secret_id)
    return render_template('secrets/secret_admin.html', secret=secret, secret_id=secret_id)
