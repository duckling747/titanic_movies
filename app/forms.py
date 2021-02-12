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
from flask_wtf.file import (
    FileField,
    FileRequired,
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
    synopsis = StringField('Synopsis')
    submit = SubmitField('Add Movie')


class SelectionForm(FlaskForm):
    select = SelectField('Select', coerce=int)
    submit = SubmitField('Add')


class DeleteSelectionForm(SelectionForm):
    submit = SubmitField('Delete')


class DisableSelectionForm(SelectionForm):
    submit = SubmitField('Disable')


class EnableSelectionForm(SelectionForm):
    submit = SubmitField('Enable')


class DeleteForm(FlaskForm):
    submit = SubmitField('Del')


class AdminRegistrationForm(RegistrationForm):
    admin = BooleanField('Is admin', default=False)


class ReviewForm(FlaskForm):
    grade = IntegerField('Grade (within range 0-5)',
        validators=[DataRequired(), NumberRange(min=0, max=5)])
    thoughts = TextAreaField('What\'d you think about it?',
        validators=[DataRequired(), Length(min=10)])
    feelings = TextAreaField('How\'d you feel about it?',
        validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send')


class NameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    

class ActorForm(NameForm):
    submit = SubmitField('Add actor')


class GenreForm(NameForm):
    submit = SubmitField('Add genre')


class LanguageForm(NameForm):
    submit = SubmitField('Add language')


class ProfileImageForm(FlaskForm):
    file = FileField('Select image file', validators=[FileRequired()])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    oldpassword = PasswordField('Old password',
        validators=[DataRequired()]
    )
    password = PasswordField('New password',
        validators=[Length(min=8), DataRequired()]
    )
    password2 = PasswordField('Confirm new password',
        validators=[EqualTo('password'), DataRequired()]
    )
    submit = SubmitField('Submit')


class EditSynopsisForm(FlaskForm):
    synopsis = TextAreaField('Synopsis')
    submit = SubmitField('Save changes')

