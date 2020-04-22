from flask import render_template, redirect, url_for, flash, Markup
from app.errors import bp

@bp.app_errorhandler(404)
def not_found_error(error):
    message = Markup(
        '<p><b>404 Not Found</b></p> <p>The requested URL was not found on the server. If you entered the URL manually '
        'please check your spelling and try again.</p>')
    flash(message, category='danger')
    return redirect(url_for('secret.index'))


@bp.app_errorhandler(500)
def internal_error(error):
    # app.logger.error(error)
    return render_template('errors/500.html'), 500
