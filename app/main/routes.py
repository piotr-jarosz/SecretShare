from flask import redirect, url_for, render_template
from app.main import bp
from flask_babel import _


@bp.route("/help/")
def help_section():
    return render_template('static/about.html')

@bp.route("/password-generator/")
def password_generator():
    return render_template('static/password_generator.html', title=_('Password generator'))
