from flask import redirect, url_for, render_template
from app.main import bp

@bp.route("/")
def index():
    return redirect(url_for('secret.index'))

@bp.route("/help/")
def help():
    pass
