hours_worked = int(input("hours worked: "))
cup_sold_per_hour = []
print("enter cups sold per hour: ")
for i in range(hours_worked):
    cup_sold_per_hour.append(int(input()))

print(cup_sold_per_hour)
total_sold = sum(cup_sold_per_hour)
average_cups_sold = round((total_sold/len(cup_sold_per_hour)), 1)

peak_hours = []

for i, csph in enumerate(cup_sold_per_hour):
    if csph > average_cups_sold:
        peak_hours.append(f'{i+8}Am')

print(f"Total: {total_sold} cups | Average: {average_cups_sold}/hr Rush hours (above average): {peak_hours}")