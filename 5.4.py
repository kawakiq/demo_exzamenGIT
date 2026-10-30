import pandas as pd
orders = pd.read_csv('Orders_analytics.csv')
items = pd.read_csv('Order_items_analytics.csv')
completed = orders[orders['order_status'] == 'completed']['order_id']

order_totals = items[items['order_id'].isin(completed)].groupby('order_id')['item_total'].sum()
Q1 = order_totals.quantile(0.25)
Q3 = order_totals.quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
filtered = order_totals[(order_totals >= lower) & (order_totals <= upper)]
print(f"Осталось: {len(filtered)}")