from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.db_models import User
import re
from time import sleep

class RegistarionFrom(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=12, max=100)])
    password_confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That user name is taken. Please, choose a different one.')

    def validate_password(form, field):
        if not re.search(r'\d', field.data):
            raise ValidationError("Password is too weak: no digit")
        if not re.search(r'[A-Z]', field.data):
            raise ValidationError("Password is too weak: no uppercase")
        if not re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r']', field.data):
            raise ValidationError("Password is too weak: no symbol")

    def validate_submit(form,field):
        sleep(0.5)

    
class LoginFrom(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

    def validate_submit(form,field):
        sleep(0.5)

class NewPasswordForm(FlaskForm):
    site_name = StringField('SiteName', validators=[DataRequired(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add')