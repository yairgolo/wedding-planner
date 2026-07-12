from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    EmailField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import URL, DataRequired, Email, Length, NumberRange, Optional


class VendorForm(FlaskForm):
    name = StringField("שם הספק", validators=[DataRequired(), Length(max=180)])
    category = SelectField(
        "קטגוריה",
        choices=[
            ("venue", "אולם"),
            ("music", "DJ / מוזיקה"),
            ("photography", "צילום"),
            ("video", "וידאו"),
            ("dress", "שמלה"),
            ("suit", "חליפה"),
            ("beauty", "איפור ושיער"),
            ("rabbi", "רב / חופה"),
            ("attraction", "אטרקציות"),
            ("decor", "עיצוב"),
            ("transport", "הסעות"),
            ("other", "אחר"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(
        "סטטוס התקשרות",
        choices=[
            ("considering", "בבדיקה"),
            ("negotiating", "במשא ומתן"),
            ("booked", "נסגר"),
            ("completed", "הושלם"),
            ("cancelled", "בוטל"),
        ],
        validators=[DataRequired()],
    )
    contact_name = StringField("איש קשר", validators=[Optional(), Length(max=180)])
    phone = StringField("טלפון", validators=[Optional(), Length(max=40)])
    email = EmailField("אימייל", validators=[Optional(), Email(), Length(max=255)])
    website_url = StringField("אתר / קישור", validators=[Optional(), URL(), Length(max=600)])
    address = StringField("כתובת", validators=[Optional(), Length(max=300)])
    agreed_amount = DecimalField(
        "סכום שסוכם", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    paid_amount = DecimalField(
        "סכום ששולם", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    next_payment_date = DateField("תשלום הבא", validators=[Optional()])
    arrival_time = TimeField("שעת הגעה לאירוע", validators=[Optional()])
    rating = IntegerField(
        "דירוג 0–5", validators=[Optional(), NumberRange(min=0, max=5)], default=0
    )
    contract_signed = BooleanField("חוזה נחתם")
    is_favorite = BooleanField("ספק מועדף / חשוב")
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("שמירה")
