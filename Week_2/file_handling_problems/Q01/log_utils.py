import re
from collections import Counter, defaultdict

def parse_lines(line):
    line = line[20:]
    splits = line.split(' ')
    level = splits[0]
    message = " ".join(splits[1:])
    return(level, message)


# def read_logs():
#     logs= defaultdict(list)
#     levels = []
#     messages = []
#     with open("Week_2/file_handling_problems/Q01/app.log", "r") as f:
#         for line in f:
#             level, message =parse_lines(line)
#             levels.append(level)
#             messages.append(message)
#             logs[level] += "".join(message)
#         levels_dict=Counter(levels) 
#         # logs = dict(zip(levels, messages))
    
#     print(levels_dict)
    print(logs)
    
def read_logs(path):
    logs = []
    with open(path, "r") as f:
        for line in f:
            logs.append(parse_lines(line))
    return logs

# logs = read_logs("Week_2/file_handling_problems/Q01/app.log")
# print(logs)