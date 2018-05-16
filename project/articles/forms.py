from wtforms import Form, StringField, validators, TextAreaField, BooleanField
from wtforms.validators import optional


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])
    p_checked = BooleanField('Make Private:', validators=[optional(), ])
    a_approve = BooleanField('Approved:', validators=[optional(), ])
