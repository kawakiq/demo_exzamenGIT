import pandas as pd
sessions = pd.read_csv('Sessions_analytics.csv')
orders = pd.read_csv('Orders_analytics.csv')

visitors = sessions.groupby('device_type')['user_id'].nunique()
completed = orders[orders['order_status'] == 'completed']
buyers_sessions = completed[['session_id']].merge(
    sessions[['session_id', 'user_id', 'device_type']], on='session_id'
)
buyers = buyers_sessions.groupby('device_type')['user_id'].nunique()

conversion = buyers / visitors
print(conversion)
print("Максимум:", conversion.idxmax())