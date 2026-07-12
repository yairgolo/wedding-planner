from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class DocumentForm(FlaskForm):
    title = StringField("שם המסמך", validators=[DataRequired(), Length(max=180)])
    category = SelectField(
        "קטגוריה",
        choices=[
            ("contract", "חוזה"),
            ("receipt", "קבלה"),
            ("quote", "הצעת מחיר"),
            ("image", "תמונה"),
            ("invitation", "הזמנה"),
            ("other", "אחר"),
        ],
        validators=[DataRequired()],
    )
    vendor_id = SelectField("ספק קשור", coerce=int, validators=[Optional()])
    file = FileField("קובץ", validators=[FileRequired()])
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("שמירה")
