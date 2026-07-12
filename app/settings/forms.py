from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import Length, NumberRange, Optional


class WeddingProfileForm(FlaskForm):
    partner_one = StringField("שם בן/בת זוג ראשון", validators=[Length(min=1, max=100)])
    partner_two = StringField("שם בן/בת זוג שני", validators=[Length(min=1, max=100)])
    event_date = DateField("תאריך לועזי", validators=[Optional()])
    hebrew_date = StringField("תאריך עברי", validators=[Optional(), Length(max=120)])
    ceremony_time = TimeField("שעת חופה", validators=[Optional()])
    venue_name = StringField("שם האולם", validators=[Optional(), Length(max=180)])
    venue_address = StringField("כתובת", validators=[Optional(), Length(max=255)])
    waze_url = StringField("קישור Waze", validators=[Optional(), Length(max=600)])
    venue_phone = StringField("טלפון האולם", validators=[Optional(), Length(max=40)])
    budget_target = DecimalField("תקציב יעד", validators=[Optional(), NumberRange(min=0)], places=2)
    meal_price = DecimalField("מחיר מנה", validators=[Optional(), NumberRange(min=0)], places=2)
    venue_capacity = IntegerField("קיבולת האולם", validators=[Optional(), NumberRange(min=0)])
    max_tables = IntegerField("מספר שולחנות מרבי", validators=[Optional(), NumberRange(min=0)])
    public_base_url = StringField("כתובת ציבורית", validators=[Optional(), Length(max=600)])
    reminder_message = TextAreaField("טקסט תזכורת", validators=[Optional(), Length(max=4000)])
    thank_you_message = TextAreaField("טקסט תודה", validators=[Optional(), Length(max=4000)])
    notes = TextAreaField("הערות כלליות", validators=[Optional(), Length(max=4000)])
    submit = SubmitField("שמירת פרופיל החתונה")
