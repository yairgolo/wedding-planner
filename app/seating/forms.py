from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class SeatingTableForm(FlaskForm):
    number = StringField("מספר שולחן", validators=[DataRequired(), Length(max=30)])
    name = StringField("שם השולחן", validators=[Optional(), Length(max=120)])
    capacity = IntegerField(
        "מספר מקומות", validators=[DataRequired(), NumberRange(min=1, max=100)], default=10
    )
    shape = SelectField(
        "צורת השולחן",
        choices=[("round", "עגול"), ("rectangle", "מלבני"), ("long", "אבירים / ארוך")],
        validators=[DataRequired()],
    )
    zone = StringField("אזור באולם", validators=[Optional(), Length(max=80)])
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("שמירת שולחן")
