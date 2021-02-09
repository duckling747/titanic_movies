from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    IntegerField,
    TextAreaField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    ValidationError,
    NumberRange,
    Length,
)

from app.models import User

from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
    ])
    password2 = PasswordField('Confirm password', validators=[
        EqualTo('password'), DataRequired()
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already in use')


class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = IntegerField('Year', validators=[
        DataRequired(),
        NumberRange(min=1500, max=datetime.today().year),
    ])
    submit = SubmitField('Add Movie')


class SelectionForm(FlaskForm):
    select = SelectField('Select', coerce=int)
    submit = SubmitField('Add')


class DeleteSelectionForm(SelectionForm):
    submit = SubmitField('Delete')


class DeleteForm(FlaskForm):
    submit = SubmitField('Del')


class AdminRegistrationForm(RegistrationForm):
    admin = BooleanField('Is admin', default=False)


class ActorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add actor')


class ReviewForm(FlaskForm):
    grade = IntegerField('Grade (within range 0-5)',
        validators=[DataRequired(), NumberRange(min=0, max=5)])
    thoughts = TextAreaField('What\'d you think about it?',
        validators=[DataRequired(), Length(min=10)])
    feelings = TextAreaField('How\'d you feel about it?',
        validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send')


class GenreForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add genre')

