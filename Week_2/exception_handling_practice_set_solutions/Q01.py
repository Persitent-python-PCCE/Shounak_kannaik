def average_order_value(total_revenue, num_orders):
    """Return the average revenue per order for a reporting period."""
    try:
        avg = total_revenue / num_orders
    except ZeroDivisionError as ze:
        return 0.0
    return round(avg, 2)

def project_revenue(current_revenue, growth_rate, periods):
    """Project revenue compounding at 'growth_rate' over N periods."""
    try:
        projected = current_revenue * (1.0 + growth_rate) ** periods
    except OverflowError:
        return ("period too large")
    return round(projected, 2)

 # --- Test cases (do not change) --
print(average_order_value(15000, 120))
print(average_order_value(15000, 0))
print(project_revenue(50000, 0.08, 5))
print(project_revenue(1e6, 8.0, 100000))