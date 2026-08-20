"""
Booking form definitions.
"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired


class BookingForm(FlaskForm):
    """Ticket booking submission form placeholder."""
    schedule_id = HiddenField("Schedule ID", validators=[DataRequired()])
    submit = SubmitField("Confirm Booking")
