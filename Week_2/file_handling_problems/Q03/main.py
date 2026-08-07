from collections import defaultdict
import csv
from math import prod

category_revenue = defaultdict(int)
product_revenue = defaultdict(int)
total_revenue = 0
n_transactions = 0
with open("Week_2/file_handling_problems/Q03/sales.csv", "r") as f:
    reader = csv.DictReader(f)
    for record in reader:
        # category reveue
        price = int(record["unit_price"])
        quantity = int(record["quantity"])
        category_revenue[record["category"]] += price*quantity
        product_revenue[record["product"]] = price*quantity
        
        #total revenue
        total_revenue += price*quantity
        n_transactions +=1
        
    #average value per transaction
    average_value_per_transaction = total_revenue/n_transactions

    
top_product = ""
top_product_sales = -1
for p, s in product_revenue.items():
    if s> top_product_sales:
        top_product = p
        top_product_sales = s

print("Revenue by Category:")
for k,v in category_revenue.items():
    print(f"\t{k}: {v}")
print(f"\ntop product: {top_product} ({top_product_sales})")
print("total revenue: ", total_revenue)
print("average/txn: ", average_value_per_transaction)


        