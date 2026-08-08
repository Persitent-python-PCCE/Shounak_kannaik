def parse_amount(raw):
    """Convert a raw text field (e.g. from a CSV) into a float amount."""
    try:
        return float(raw)
    except ValueError:
        return f'"{raw}" is a non-numeric value'

def column_total(values):
    """Sum a numeric column. A stray string entry raises TypeError."""
    try:
        return sum(values)
    except TypeError:
        for i in values:
            if type(i) != int:
                return f'"{i}" is a non-numeric value'

print(parse_amount("1999.50"))
print(parse_amount("N/A"))
print(column_total([100, 250, 75]))
print(column_total([100, "250", 75]))