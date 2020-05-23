from flask import flash as flask_flash


def flash(message: str, category: str = 'info'): flask_flash(message, category=category)
