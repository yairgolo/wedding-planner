from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("אימייל", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("סיסמה", validators=[DataRequired(), Length(min=8, max=128)])
    remember = BooleanField("זכור אותי")
    submit = SubmitField("כניסה למערכת")
