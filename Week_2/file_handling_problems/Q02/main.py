from redaction_config import redact

redacted_text = redact("Week_2/file_handling_problems/Q02/report.txt")

# print(replacement_count)
with open("Week_2/file_handling_problems/Q02/report_redacted.txt", "w") as f:
    f.write(redacted_text)


with open("Week_2/file_handling_problems/Q02/report_redacted.txt", "r") as f:
    for line in f:
        print(line)
        
