from wtforms import Form, StringField, PasswordField, validators, IntegerField, TextAreaField, BooleanField
from wtforms.validators import optional


# U_data Form Class
class UserForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    admin = IntegerField('Admin')


# Admin user edit Form Class
class EditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    admin = IntegerField('Admin')


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])
    p_checked = BooleanField('Make Private:', validators=[optional(), ])
    a_approve = BooleanField('Approved:', validators=[optional(), ])
