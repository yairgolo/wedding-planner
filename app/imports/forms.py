from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, SubmitField


class GuestImportForm(FlaskForm):
    file = FileField(
        "קובץ מוזמנים",
        validators=[FileRequired(), FileAllowed(["xlsx", "csv"], "יש להעלות Excel או CSV")],
    )
    duplicate_mode = SelectField(
        "טיפול ברשומות קיימות",
        choices=[
            ("update", "עדכן לפי UUID / מזהה / טלפון (מומלץ)"),
            ("skip", "דלג על רשומות קיימות לפי UUID / מזהה / טלפון"),
            ("import", "ייבא כרשומות חדשות כאשר אין UUID או מזהה"),
        ],
        default="update",
    )
    submit = SubmitField("ייבוא מוזמנים")
