from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class BudgetTargetForm(FlaskForm):
    budget_target = DecimalField(
        "תקציב יעד", validators=[DataRequired(), NumberRange(min=0)], places=2
    )
    submit = SubmitField("עדכון תקציב")


class BudgetItemForm(FlaskForm):
    name = StringField("שם ההוצאה", validators=[DataRequired(), Length(max=180)])
    category = SelectField(
        "קטגוריה",
        choices=[
            ("venue", "אולם ואוכל"),
            ("photography", "צילום"),
            ("music", "מוזיקה ו-DJ"),
            ("clothing", "לבוש"),
            ("beauty", "איפור ושיער"),
            ("design", "עיצוב והזמנות"),
            ("attractions", "אטרקציות"),
            ("transport", "הסעות ורכב"),
            ("home", "בית"),
            ("other", "אחר"),
        ],
        validators=[DataRequired()],
    )
    supplier_name = StringField("ספק", validators=[Optional(), Length(max=180)])
    planned_amount = DecimalField(
        "סכום מתוכנן", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    actual_amount = DecimalField(
        "סכום שסוכם בפועל", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    paid_amount = DecimalField(
        "כמה שולם", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    status = SelectField(
        "סטטוס",
        choices=[
            ("planned", "מתוכנן"),
            ("agreed", "נסגר"),
            ("partial", "שולם חלקית"),
            ("paid", "שולם במלואו"),
            ("cancelled", "בוטל"),
        ],
        validators=[DataRequired()],
    )
    due_date = DateField("מועד תשלום הבא", validators=[Optional()])
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("שמירה")
