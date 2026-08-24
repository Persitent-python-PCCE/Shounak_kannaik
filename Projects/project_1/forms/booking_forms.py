
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional


class BookingForm(FlaskForm):
    schedule_id = HiddenField("Schedule ID", validators=[DataRequired()])
    seat_ids = HiddenField("Seat IDs", validators=[DataRequired()])
    payment_mode_id = SelectField("Payment Mode", coerce=int, validators=[Optional()])
    submit = SubmitField("Proceed to Payment")
