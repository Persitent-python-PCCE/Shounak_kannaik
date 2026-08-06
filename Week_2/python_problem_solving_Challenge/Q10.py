inv = [
    ("Masala Chai", "Tea", 5, 20),
    ("Green Tea", "Tea", 15, 30),
    ("Samosa", "Snack", 8, 15),
    ("Biscuit", "Snack", 25, 10),
]

def inventory_report(inv, gst=0.05, **filters):        
    # unique categories
    get_categories = lambda x: x[1]
    all_categories = set(map(get_categories, inv))
    print(all_categories)
    
    # low stock
    low_stock = lambda x: x[2]<10
    low_stock = list(filter(low_stock, inv))
    print(low_stock)
    
    #price with gst
    calc_price = lambda x: {x[0] :x[3]+(x[3]*gst)}
    price_with_gst = map(calc_price, inv)
    print(list(price_with_gst))

    #filters
    if filters:
        print(filters)
        filtered_items = []
        for item, category, stock, u_price in inv:
            match = True
            if "category" in filters:
                if category != filters["category"]:
                    match = False
            if "item" in filters:
                if item != filters["item"]:
                    match = False
            if "max_price" in filters:
                if u_price >filters["max_price"]:
                    match = False
            if "min_price" in filters:
                        if u_price <filters["min_price"]:
                            match = False
            if match:
                filtered_items.append(item)
        print(filtered_items) if filtered_items else print("No Matching item") 
                
                
inventory_report(inv=inv, category="Snack",max_price=15)