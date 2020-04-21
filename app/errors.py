from flask import render_template, redirect, url_for, flash, Markup
from app import app


@app.errorhandler(404)
def not_found_error(error):
    message = Markup(
        '<p><b>404 Not Found</b></p> <p>The requested URL was not found on the server. If you entered the URL manually '
        'please check your spelling and try again.</p>')
    flash(message, category='danger')
    return redirect(url_for('index')), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(error)
    return render_template('500.html'), 500
