from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign me up')


class PostForm(FlaskForm):
    post_text = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Post')


class RateForm(FlaskForm):
    post_id = HiddenField()
    like = HiddenField()
