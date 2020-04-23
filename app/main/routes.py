from flask import redirect, url_for, render_template
from app.main import bp

@bp.route("/")
def index():
    return redirect(url_for('secret.index'))

@bp.route("/help/")
def help():
    return render_template('static/about.html')

@bp.route("/password-generator/")
def password_generator():
    return render_template('static/password_generator.html')
