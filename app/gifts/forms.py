from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class GiftForm(FlaskForm):
    guest_name = StringField("שם נותן המתנה", validators=[DataRequired(), Length(max=180)])
    gift_type = SelectField(
        "סוג מתנה",
        choices=[
            ("cash", "מזומן"),
            ("check", "צ׳ק"),
            ("transfer", "העברה"),
            ("item", "מתנה פיזית"),
            ("other", "אחר"),
        ],
        validators=[DataRequired()],
    )
    amount = DecimalField(
        "שווי / סכום", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    description = StringField("תיאור המתנה", validators=[Optional(), Length(max=500)])
    received_date = DateField("תאריך קבלה", validators=[Optional()])
    thank_you_sent = BooleanField("נשלחה הודעת תודה")
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("שמירה")
