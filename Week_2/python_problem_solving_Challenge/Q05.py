order = [("Masala Chai", 3, 20), ("Samosa", 2, 15), ("Green Tea", 1, 30)]
func = lambda ord: (float(ord[2])+(float(ord[2])*0.05))*ord[1]
line_totals = list(map(func, order))
print(f'Line totals (incl. GST): {line_totals}')
print(f'total: {sum(line_totals)}')