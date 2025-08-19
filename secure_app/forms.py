from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('password', validators=[DataRequired(), Length(max=128)])

class CommentForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(max=64)])
    comment = TextAreaField('comment', validators=[DataRequired(), Length(max=2000)])
