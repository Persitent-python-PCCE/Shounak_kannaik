"""
Validation helper functions.
"""

import re


def validate_email(email_str):
    """
    Validate an email address format.

    :param email_str: str - Email address to validate
    :return: bool - True if format is valid, False otherwise
    """
    if not email_str:
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email_str))
