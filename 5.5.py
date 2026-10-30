import pandas as pd
orders = pd.read_csv('Orders_analytics.csv')
items = pd.read_csv('Order_items_analytics.csv')

completed_ids = orders[orders['order_status'] == 'completed']['order_id']
data = items[items['order_id'].isin(completed_ids)]
r = data['discount_percent'].corr(data['quantity'])
print(f"r = {r:.3f}")