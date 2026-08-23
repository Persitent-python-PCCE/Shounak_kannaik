"""
Event management form definitions.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional, Length


class EventForm(FlaskForm):
    """Event creation and update form."""
    name = StringField("Event Name", validators=[DataRequired(), Length(max=255)])
    about = TextAreaField("About / Description", validators=[Optional()])
    event_type_id = SelectField("Event Type", coerce=int, validators=[Optional()])
    age_rating = SelectField(
        "Age Rating",
        choices=[
            ("All Ages", "All Ages (U/G)"),
            ("PG", "Parental Guidance (PG)"),
            ("UA 13+", "UA 13+"),
            ("UA 16+", "UA 16+"),
            ("18+ / A", "Adults Only (18+ / A)")
        ],
        default="All Ages"
    )
    poster_image = FileField(
        "Poster Image (Optional - PNG, JPG, WEBP)",
        validators=[
            FileAllowed(["png", "jpg", "jpeg", "webp"], "Allowed formats: PNG, JPG, JPEG, WEBP")
        ]
    )

    # Optional inline schedule setup
    venue_id = SelectField("Host Venue", coerce=int, validators=[Optional()])
    start_datetime = DateTimeLocalField("Start Date & Time", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    end_datetime = DateTimeLocalField("End Date & Time", format="%Y-%m-%dT%H:%M", validators=[Optional()])

    submit = SubmitField("Save Event")
