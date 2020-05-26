from flask import redirect, url_for, render_template
from app.manager import bp
from flask_babel import _


@bp.route('/user')
def user_manager():
    return render_template('manager/user.html')

@bp.route('/users')
def users_manager():
    return render_template('manager/users.html')

@bp.route('/settings')
def settings_manager():
    return render_template('manager/settings.html')\

@bp.route('/secrets')
def secrets_manager():
    return render_template('manager/secrets.html')


