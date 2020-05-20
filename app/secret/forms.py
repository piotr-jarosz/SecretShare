from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import TextAreaField, PasswordField, SubmitField, SelectField, StringField
from wtforms.validators import DataRequired, Email
from flask_babel import lazy_gettext as _l
from config import Config


class SecretForm(FlaskForm):
    secret = TextAreaField(_l('Secret'), validators=[DataRequired()])
    passphrase = PasswordField(_l('Passphrase'))
    ttl = SelectField(_l('Burn after:'), choices=[('1', _l('1 hour')), ('3', _l('3 hours')), ('6', _l('6 hours')),
                                                  ('12', _l('12 hours')), ('24', _l('24 hours'))],
                      validators=[DataRequired()])
    submit = SubmitField('Create secret!')
    if Config.RECAPTCHA_PUBLIC_KEY:
        recaptcha = RecaptchaField()


class BurnSecretForm(FlaskForm):
    submit = SubmitField(_l('Burn the Secret!'))


class ReadSecretForm(FlaskForm):
    passphrase = PasswordField(_l('Passphrase'))
    submit = SubmitField(_l('Open my secret!'))


class SendSecretLink(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit_email = SubmitField(_l('Send!'))


class SendPassphrase(FlaskForm):
    country_code = SelectField(_l('Country code'), validators=[DataRequired()], choices=[('PL', '+48'), ])
    msisdn = StringField(_l('Cellphone number'), validators=[DataRequired()])
    submit_sms = SubmitField(_l('Send!'))
