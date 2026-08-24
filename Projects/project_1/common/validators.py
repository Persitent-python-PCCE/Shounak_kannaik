
import re


def validate_email(email_str):
    if not email_str:
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email_str))
