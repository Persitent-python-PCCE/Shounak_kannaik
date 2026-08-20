"""
Event management form definitions.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class EventForm(FlaskForm):
    """Event creation and update form placeholder."""
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Save Event")
