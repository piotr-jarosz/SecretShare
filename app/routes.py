from typing import Optional, Dict, Union, Any

from flask import render_template, flash, redirect, url_for
from app.forms import SecretForm
from app import app
from models import Secret
from json import dumps

@app.route("/secret/", methods=['GET', 'POST'])
def index():
    form = SecretForm()
    if form.validate_on_submit():
        flash('Secret: {}, Passphrase: {}, ttl={}'.format(
            form.secret.data, form.passphrase.data, form.ttl.data))
        secret = Secret(form.secret.data, form.ttl.data, form.passphrase.data)
        secret_id = secret.save()
        return redirect('/secret/' + secret_id + '/admin')
    return render_template('index.html', title='Create your secret now!', form=form)


@app.route('/')
def index_redirect():
    return redirect(url_for('index'))


@app.route("/secret/<secret_id>")
def read_secret(secret_id):
    secret = Secret.read(secret_id)
    return render_template('secret.html', secret=secret, secret_id=secret_id)


@app.route("/secret/<secret_id>/show")
def show_secret(secret_id):
    secret = Secret.read(secret_id=secret_id)
    if secret:
        secret = dumps(secret)
        Secret.destroy(secret_id)
    else:
        secret = None
    return secret


@app.route("/secret/<secret_id>/admin")
def secret_admin(secret_id, methods=['GET', 'POST']):
    secret = Secret.read(secret_id=secret_id)
    return render_template('secret_admin.html', secret=secret, secret_id=secret_id)
