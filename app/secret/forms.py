from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l


class SecretForm(FlaskForm):
    secret = TextAreaField(_l('Secret'), validators=[DataRequired()])
    passphrase = PasswordField(_l('Passphrase'))
    ttl = SelectField(_l('Burn after:'), choices=[('1', _l('1 hour')), ('3', _l('3 hours')), ('6', _l('6 hours')),
                                              ('12', _l('12 hours')), ('24', _l('24 hours'))])
    submit = SubmitField('Create secret!')


class ReadSecretForm(FlaskForm):
    passphrase = PasswordField(_l('Passphrase'))
    submit = SubmitField(_l('Open my secret!'))
