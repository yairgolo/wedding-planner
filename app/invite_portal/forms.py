from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional

SIDE_CHOICES = [("groom", "צד החתן"), ("bride", "צד הכלה")]
SALUTATION_CHOICES = [
    ("", "בחירת צורת פנייה…"),
    ("male", "זכר"),
    ("female", "נקבה"),
    ("plural", "רבים"),
]


class PortalLoginForm(FlaskForm):
    email = StringField("אימייל מנהל", validators=[DataRequired(), Length(max=255)])
    password = PasswordField("סיסמה", validators=[DataRequired()])
    submit = SubmitField("כניסת מנהל")


class SenderForm(FlaskForm):
    name = StringField("שם השולח", validators=[DataRequired(), Length(max=120)])
    role = StringField("תפקיד", validators=[DataRequired(), Length(max=120)])
    side = SelectField("צד", choices=SIDE_CHOICES, validators=[DataRequired()])
    male_template = TextAreaField("נוסח לזכר", validators=[DataRequired(), Length(max=5000)])
    female_template = TextAreaField("נוסח לנקבה", validators=[DataRequired(), Length(max=5000)])
    plural_template = TextAreaField("נוסח לרבים", validators=[DataRequired(), Length(max=5000)])
    is_active = BooleanField("הקישור פעיל", default=True)
    submit = SubmitField("שמירה")


class PortalGuestForm(FlaskForm):
    first_name = StringField("שם פרטי / פנייה", validators=[DataRequired(), Length(max=120)])
    last_name = StringField("שם משפחה", validators=[Optional(), Length(max=120)])
    phone = StringField("טלפון WhatsApp", validators=[Optional(), Length(max=32)])
    side = SelectField("צד", choices=SIDE_CHOICES, validators=[DataRequired()])
    salutation = SelectField("צורת פנייה", choices=SALUTATION_CHOICES, validators=[DataRequired()])
    invitation_decision = SelectField(
        "החלטת הזמנה",
        choices=[("invited", "כן, מזמינים"), ("undecided", "בסימן שאלה")],
        default="invited",
        validators=[DataRequired()],
    )
    group_name = StringField("קבוצה", validators=[Optional(), Length(max=120)])
    notes = TextAreaField("הערה", validators=[Optional()])
    submit = SubmitField("שמירת מוזמן")


class ImageForm(FlaskForm):
    image = FileField("תמונת ההזמנה", validators=[FileAllowed(["jpg", "jpeg", "png", "webp"])])
    submit = SubmitField("העלאת תמונה")


class MessageForm(FlaskForm):
    male_template = TextAreaField("נוסח לזכר", validators=[DataRequired(), Length(max=5000)])
    female_template = TextAreaField("נוסח לנקבה", validators=[DataRequired(), Length(max=5000)])
    plural_template = TextAreaField("נוסח לרבים", validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField("שמירת הנוסחים שלי")
