"""
Flask-WTF Forms package initialization.
"""

from forms.auth_forms import LoginForm, RegisterForm
from forms.event_forms import EventForm
from forms.booking_forms import BookingForm

__all__ = [
    "LoginForm",
    "RegisterForm",
    "EventForm",
    "BookingForm",
]
