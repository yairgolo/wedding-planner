from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SelectField, SubmitField


class GuestImportForm(FlaskForm):
    file = FileField(
        "קובץ מוזמנים",
        validators=[FileRequired(), FileAllowed(["xlsx", "csv"], "יש להעלות Excel או CSV")],
    )
    duplicate_mode = SelectField(
        "טיפול בכפילויות", choices=[("skip", "דלג לפי מספר טלפון"), ("import", "ייבא בכל מקרה")]
    )
    submit = SubmitField("ייבוא מוזמנים")
