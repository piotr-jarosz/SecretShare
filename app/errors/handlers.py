from flask import render_template, redirect, url_for, flash, Markup, request, current_app
from app.errors import bp
from flask_babel import _


@bp.app_errorhandler(404)
def not_found_error(error):
    message = Markup(_(
        '<p><b>404 Not Found</b></p> <p>The requested URL: ' +
        '<a href="{path}">{path}</i></a> was not found on the server. '.format(path=request.base_url) +
        'If you entered the URL manually ' +
        'please check your spelling and try again.</p>'))
    flash(message, category='danger')
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    current_app.logger.error(error)
    return render_template('errors/500.html'), 500
