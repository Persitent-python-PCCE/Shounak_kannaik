import re

def redact (path):
    # sensitive_words = [r"Titan", r"Acme corp"]
    sensitive_pattern = r'Titan|Acme corp'
    op= ""
    with open(path, "r") as f:
        for line in f:
            op += re.sub(sensitive_pattern,"[Redacted]", line, flags=re.IGNORECASE)
    return op
