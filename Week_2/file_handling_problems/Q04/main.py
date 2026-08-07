from collections import defaultdict
import csv
from hashlib import new

def get_grade(avg):
    match avg:
        case avg if avg>=90:
            return "A"
        case avg if avg>=75 and avg<89:
            return "B"
        case avg if avg>=60 and avg<74:
            return "C"
        case avg if avg>=40 and avg<59:
            return "D"
        case avg if avg<40:
            return "F"

reports=[]
top_avg = -1
class_topper = ""
pass_count =0
fail_count = 0

with open("Week_2/file_handling_problems/Q04/students.csv", "r") as f:
    reader = csv.DictReader(f)
    for record in reader:
        # report calculations
        total = int(record["maths"])+int(record["physics"])+int(record["chemistry"])
        average = total/3
        grade = get_grade(average)
        
        # pass fail count calc
        if grade != "F":
            pass_count += 1
        else:
            fail_count += 1
        
        # class topper
        if average > top_avg:
            top_avg = average
            class_topper = record["name"]
            
        report = {
            "total" :total,
            "average": round(average, 2),
            "grade": grade
        }
        record.update(report)
        reports.append(record)
    
# for report in reports:
#     print(report)

fields = ["roll_no", "name", "maths", "physics", "chemistry", "total", "average", "grade"]
with open("Week_2/file_handling_problems/Q04/students_results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(reports)

with open("Week_2/file_handling_problems/Q04/students_results.csv", "r", newline="") as f:
    for line in f:
        print(line)

print("Processed 4 students -> students_result.csv")
print(f"class topper: {class_topper} (avg: {round(top_avg, 2)})")
print(f'passed: {pass_count} | failed: {fail_count}')
    