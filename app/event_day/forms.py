from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length, Optional


class ScheduleItemForm(FlaskForm):
    time = TimeField("שעה", validators=[DataRequired()])
    title = StringField("מה קורה", validators=[DataRequired(), Length(max=180)])
    owner = StringField("אחראי", validators=[Optional(), Length(max=180)])
    notes = StringField("הערה", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("הוספה ללוח הזמנים")


class MusicRequestForm(FlaskForm):
    title = StringField("שיר / אמן", validators=[DataRequired(), Length(max=180)])
    artist = StringField("אמן / גרסה", validators=[Optional(), Length(max=180)])
    moment = SelectField(
        "מתי לנגן",
        choices=[
            ("ceremony", "חופה"),
            ("entrance", "כניסה"),
            ("first_dance", "ריקוד ראשון"),
            ("party", "רחבה"),
            ("avoid", "לא לנגן"),
        ],
        validators=[DataRequired()],
    )
    notes = StringField("הערה ל-DJ", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("הוספה לפלייליסט")
