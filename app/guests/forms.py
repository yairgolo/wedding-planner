from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

SIDE_CHOICES = [("groom", "צד חתן"), ("bride", "צד כלה"), ("shared", "משותף")]
RSVP_CHOICES = [
    ("pending", "ממתין"),
    ("confirmed", "מגיע"),
    ("declined", "לא מגיע"),
    ("maybe", "אולי"),
]
DIET_CHOICES = [
    ("regular", "רגיל"),
    ("vegetarian", "צמחוני"),
    ("vegan", "טבעוני"),
    ("gluten_free", "ללא גלוטן"),
    ("child", "מנת ילדים"),
    ("other", "אחר"),
]


class GuestForm(FlaskForm):
    first_name = StringField("שם פרטי", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("שם משפחה", validators=[Optional(), Length(max=100)])
    phone = StringField("טלפון", validators=[Optional(), Length(max=32)])
    email = EmailField("אימייל", validators=[Optional(), Email(), Length(max=255)])
    side = SelectField("צד", choices=SIDE_CHOICES, validators=[DataRequired()])
    group_name = StringField("קבוצה", validators=[Optional(), Length(max=100)])
    family_id = SelectField("משפחה", coerce=int, validators=[Optional()])
    invited_count = IntegerField(
        "כמות מוזמנים", validators=[DataRequired(), NumberRange(min=1, max=30)], default=1
    )
    confirmed_count = IntegerField(
        "כמות שאישרה", validators=[InputRequired(), NumberRange(min=0, max=30)], default=0
    )
    rsvp_status = SelectField("סטטוס RSVP", choices=RSVP_CHOICES, validators=[DataRequired()])
    is_vip = BooleanField("VIP")
    diet = SelectField("תזונה", choices=DIET_CHOICES, validators=[DataRequired()])
    diet_notes = StringField("פירוט תזונה", validators=[Optional(), Length(max=255)])
    table_number = StringField("מספר שולחן", validators=[Optional(), Length(max=30)])
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("שמירה")

    def validate_confirmed_count(self, field):
        invited = self.invited_count.data or 0
        if field.data is not None and field.data > invited:
            raise ValidationError("כמות המאשרים לא יכולה להיות גדולה מכמות המוזמנים.")


class FamilyForm(FlaskForm):
    name = StringField("שם המשפחה", validators=[DataRequired(), Length(max=160)])
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("הוספת משפחה")


class RSVPForm(FlaskForm):
    status = SelectField(
        "האם תגיעו?",
        choices=[
            ("confirmed", "בשמחה, מגיעים"),
            ("declined", "לצערנו לא נוכל להגיע"),
            ("maybe", "עדיין לא בטוחים"),
        ],
        validators=[DataRequired()],
    )
    confirmed_count = IntegerField(
        "כמה מגיעים?", validators=[InputRequired(), NumberRange(min=0, max=30)], default=1
    )
    diet_notes = StringField("הערות תזונה", validators=[Optional(), Length(max=255)])
    message = TextAreaField("ברכה או הערה", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("שליחת אישור הגעה")
