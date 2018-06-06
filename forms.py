from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, DateField, FloatField
from wtforms.validators import (Email, DataRequired ,Regexp,
                                ValidationError, Length,EqualTo)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
         raise ValidationError("User with that name exists")


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("exists")


class RegisterForm(Form):
             email  = StringField(
                 'Email',
                 validators=[
                      DataRequired(),
                      Email(),
                      email_exists
                 ]
             )
             password = PasswordField(
                 'Password',
                 validators = [
                     DataRequired(),
                     Length(min=2),
                     EqualTo('password2', 'Message does not match')

                 ]
             )
             password2 = PasswordField(
                'Confirm password',
                validators=[
                    DataRequired()
                ]
             )

class LoginForm(Form):
     email = StringField('Email', validators=[DataRequired(), Email()])
     password = PasswordField('Password', validators=[DataRequired()])


class EntryForm(Form):
    title     = StringField("Title", validators=[DataRequired()])
    date      = DateField("mm/dd/yyyy", format='%m/%d/%Y', validators=[DataRequired()])
    timespent =FloatField ("Time spent", validators=[DataRequired()])
    learned    = StringField("learned", validators=[DataRequired()])
    resources = TextAreaField("Resources to remember", validators=[DataRequired()], render_kw={"rows": 20, "cols": 50})

