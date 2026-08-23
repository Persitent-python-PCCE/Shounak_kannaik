"""
Venue management form definitions.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class VenueForm(FlaskForm):
    """Venue creation and edit form."""
    name = StringField("Venue Name", validators=[DataRequired(), Length(max=255)])
    address = StringField("Address", validators=[DataRequired(), Length(max=255)])
    city = StringField("City", validators=[DataRequired(), Length(max=255)])
    state = StringField("State", validators=[DataRequired(), Length(max=255)])
    country = StringField("Country", validators=[DataRequired(), Length(max=255)])
    capacity = IntegerField("Capacity", validators=[Optional(), NumberRange(min=1, message="Capacity must be at least 1")])
    submit = SubmitField("Save Venue")
