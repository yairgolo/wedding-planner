from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class InvitationSettingsForm(FlaskForm):
    message_template = TextAreaField(
        "טקסט ההזמנה",
        validators=[DataRequired(), Length(max=4000)],
    )
    image = FileField(
        "תמונת ההזמנה",
        validators=[FileAllowed(["jpg", "jpeg", "png", "webp"], "יש להעלות קובץ תמונה")],
    )
    submit = SubmitField("שמירת הגדרות")
