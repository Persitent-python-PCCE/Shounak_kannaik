
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SelectField, SubmitField


class DocumentUploadForm(FlaskForm):
    doc_type = SelectField(
        "Document Type",
        choices=[
            ("Govt ID", "Government ID"),
            ("Aadhaar", "Aadhaar Card"),
            ("Passport", "Passport"),
            ("PAN Card", "PAN Card"),
            ("Driving License", "Driving License")
        ],
        default="Govt ID"
    )
    document = FileField(
        "Select File (PDF, PNG, JPG)",
        validators=[
            FileRequired(message="Please select a document file to upload."),
            FileAllowed(["pdf", "png", "jpg", "jpeg"], "Allowed formats: PDF, PNG, JPG, JPEG")
        ]
    )
    submit = SubmitField("Upload Document")
