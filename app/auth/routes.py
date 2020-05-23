from flask import render_template, redirect, url_for, request, abort, current_app
from app.helpers import flash
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, SetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email, send_account_activation_token


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_app.config['LOGIN_DISABLED']:
        abort(404)

    if current_user.is_authenticated:
        return redirect(url_for('secret.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), category='danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('secret.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form, not_register=current_app.config['REGISTRATION_DISABLED'])


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('secret.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_app.config['REGISTRATION_DISABLED'] or current_app.config['LOGIN_DISABLED']:
        abort(404)

    if current_user.is_authenticated:
        return redirect(url_for('secret.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        send_account_activation_token(user)
        flash(_('Congratulations, you are now a registered user! Check your e-mail to activate account.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'),
                           form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_app.config['LOGIN_DISABLED']:
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for('secret.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/passwd/<token>', methods=['GET', 'POST'])
def set_password(token):
    if current_user.is_authenticated:
        flash(_('Looks like you have already activated your account.'))
        return redirect(url_for('secret.index'))
    user = User.verify_set_password_token(token)
    if not user:
        abort(404)

    form = SetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been setup.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/set_password.html', form=form)
