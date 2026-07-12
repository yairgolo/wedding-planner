from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class TaskForm(FlaskForm):
    title = StringField("שם המשימה", validators=[DataRequired(), Length(max=220)])
    category = SelectField(
        "קטגוריה",
        choices=[
            ("wedding", "חתונה"),
            ("event_day", "יום החתונה"),
            ("home", "בית"),
            ("documents", "מסמכים"),
            ("payments", "תשלומים"),
            ("guests", "מוזמנים"),
            ("seating", "הושבה"),
            ("shopping", "קניות"),
            ("general", "כללי"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(
        "סטטוס",
        choices=[("todo", "לביצוע"), ("doing", "בתהליך"), ("done", "הושלם")],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "עדיפות",
        choices=[("low", "נמוכה"), ("medium", "רגילה"), ("high", "גבוהה"), ("urgent", "דחופה")],
        validators=[DataRequired()],
    )
    due_date = DateField("תאריך יעד", validators=[Optional()])
    assigned_to = StringField("אחראי/ת", validators=[Optional(), Length(max=120)])
    related_vendor_id = SelectField("ספק קשור", coerce=int, validators=[Optional()], choices=[])
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=3000)])
    submit = SubmitField("שמירה")
