from collections import Counter, defaultdict
from log_utils import read_logs

logs = read_logs("Week_2/file_handling_problems/Q01/app.log")
log_dict= defaultdict(list)

for key, value in logs:
    log_dict[key].append(value)

log_dict = dict(log_dict)

error_messages = []
level_count = {}
for k, v in log_dict.items():
    level_count[k] = len(v)
    if k == "ERROR":
        error_messages = v

print(level_count)

for category, count in level_count.items():
    print(f'{category}: {count}')
        
print("errors found: ")
for e in error_messages:
    print(f'- {e}')