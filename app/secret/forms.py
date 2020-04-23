from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SecretForm(FlaskForm):
    secret = TextAreaField('Secret', validators=[DataRequired()])
    passphrase = PasswordField('Passphrase')
    ttl = SelectField('Burn after:', choices=[('1', '1 hour'), ('3', '3 hours'), ('6', '6 hours'),
                                              ('12', '12 hours'), ('24', '24 hours')])
    submit = SubmitField('Create secret!')


class ReadSecretForm(FlaskForm):
    passphrase = PasswordField('Passphrase')
    submit = SubmitField('Open my secret!')
