
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, SubmitField
from wtforms.validators import DataRequired


class PaymentForm(FlaskForm):
    booking_id = HiddenField("Booking ID", validators=[DataRequired()])
    payment_mode_id = SelectField("Payment Mode", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Generate Payment QR")
