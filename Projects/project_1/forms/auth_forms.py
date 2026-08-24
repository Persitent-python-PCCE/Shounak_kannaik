
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Regexp, Length, Optional, EqualTo

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
PHONE_REGEX = r"^\+?[0-9]{7,15}$"


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Regexp(EMAIL_REGEX, message="Please enter a valid email address."),
            Length(max=100)
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long."),
            Regexp(
                PASSWORD_REGEX,
                message="Password must contain at least 1 capital letter, 1 number, and 1 special character."
            )
        ]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )
    phone_no = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Regexp(PHONE_REGEX, message="Please enter a valid numeric phone number (7-15 digits, optional '+' prefix)."),
            Length(max=20)
        ]
    )
    doc_type = SelectField(
        "ID Document Type",
        choices=[
            ("Govt ID", "Government ID"),
            ("Aadhaar", "Aadhaar Card"),
            ("Passport", "Passport"),
            ("PAN Card", "PAN Card"),
            ("Driving License", "Driving License")
        ],
        default="Govt ID",
        validators=[Optional()]
    )
    id_document = FileField(
        "Identity Document (PDF, PNG, JPG - Optional)",
        validators=[
            Optional(),
            FileAllowed(["pdf", "png", "jpg", "jpeg"], "Allowed file formats: PDF, PNG, JPG, JPEG")
        ]
    )
    submit = SubmitField("Create Account")


class UserEditForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Regexp(EMAIL_REGEX, message="Please enter a valid email address."),
            Length(max=100)
        ]
    )
    phone_no = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Regexp(PHONE_REGEX, message="Please enter a valid numeric phone number (7-15 digits, optional '+' prefix)."),
            Length(max=20)
        ]
    )
    role = SelectField(
        "Role",
        choices=[
            ("customer", "Customer"),
            ("admin", "Admin")
        ],
        default="customer",
        validators=[DataRequired()]
    )
    is_active = BooleanField("Account Active Status", default=True)
    submit = SubmitField("Save Changes")
