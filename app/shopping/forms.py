from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import URL, DataRequired, Length, NumberRange, Optional


class ShoppingItemForm(FlaskForm):
    name = StringField("שם הפריט", validators=[DataRequired(), Length(max=180)])
    category = SelectField(
        "קטגוריה",
        choices=[
            ("wedding", "חתונה"),
            ("home", "בית"),
            ("clothing", "בגדים"),
            ("gifts", "מתנות"),
            ("general", "כללי"),
            ("other", "אחר"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(
        "סטטוס",
        choices=[
            ("planned", "מתוכנן"),
            ("ordered", "הוזמן"),
            ("purchased", "נקנה"),
            ("cancelled", "בוטל"),
        ],
        validators=[DataRequired()],
    )
    priority = SelectField(
        "עדיפות",
        choices=[("low", "נמוכה"), ("medium", "רגילה"), ("high", "גבוהה"), ("urgent", "דחופה")],
        validators=[DataRequired()],
    )
    quantity = IntegerField("כמות", validators=[DataRequired(), NumberRange(min=1, max=10000)])
    estimated_price = DecimalField(
        "מחיר משוער ליחידה", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    actual_price = DecimalField(
        "מחיר בפועל ליחידה", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    store_name = StringField("חנות / ספק", validators=[Optional(), Length(max=180)])
    product_url = StringField("קישור למוצר", validators=[Optional(), URL(), Length(max=600)])
    due_date = DateField("תאריך יעד", validators=[Optional()])
    is_wishlist = BooleanField("Wishlist — עדיין לא החלטנו אם לקנות")
    notes = TextAreaField("הערות", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("שמירה")
