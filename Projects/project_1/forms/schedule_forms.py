"""
Schedule management form definitions.
"""

from flask_wtf import FlaskForm
from wtforms import SelectField, DateTimeLocalField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class ScheduleForm(FlaskForm):
    """Event schedule creation and update form."""
    event_id = SelectField("Event", coerce=int, validators=[DataRequired()])
    venue_id = SelectField("Venue", coerce=int, validators=[DataRequired()])
    start_datetime = DateTimeLocalField("Start Date & Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    end_datetime = DateTimeLocalField("End Date & Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[
            ("Scheduled", "Scheduled"),
            ("Rescheduled", "Rescheduled"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ],
        default="Scheduled"
    )
    submit = SubmitField("Save Schedule")
