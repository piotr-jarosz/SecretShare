import json
from flask import render_template, flash as flask_flash, redirect, url_for, request
from app.main.forms import SecretForm, ReadSecretForm
from app.main import bp
from app.models import Secret
from functools import partial

flash = partial(flask_flash, category='info')

@bp.route("/", methods=['GET', 'POST'])
def index():
    form = SecretForm()
    if form.validate_on_submit():
        flash('Secret created!')
        secret = Secret(form.secret.data, form.ttl.data, passphrase=form.passphrase.data)
        secret_id = secret.save()
        return redirect(url_for('main.secret_admin', secret_id=secret_id))
    return render_template('index.html', title='Create your secret now!', form=form)


@bp.route("/<secret_id>", methods=['GET', 'POST', 'DELETE'])
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
    return render_template('secret.html', passphrase=passphrase, secret_id=secret_id, form=form)


@bp.route("/<secret_id>/admin")
@bp.route("/<secret_id>/admin/")
def secret_admin(secret_id):
    secret = Secret.load(secret_id)
    return render_template('secret_admin.html', secret=secret, secret_id=secret_id)
