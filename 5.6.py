import pandas as pd
orders = pd.read_csv('Orders_analytics.csv')
items = pd.read_csv('Order_items_analytics.csv')
models = pd.read_csv('Shoe_models_analytics.csv')
completed_ids = orders[orders['order_status'] == 'completed']['order_id']

data = (
    items[items['order_id'].isin(completed_ids)]
    .merge(
        models[['model_id', 'category']],
        on='model_id'
    )
)

result = data.groupby('category')['quantity'].sum().sort_values(ascending=False)
print(result)
print("Максимум:", result.idxmax())
