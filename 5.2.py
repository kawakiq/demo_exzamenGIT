import pandas as pd
sessions = pd.read_csv('Sessions_analytics.csv')
orders = pd.read_csv('Orders_analytics.csv')

sessions['session_start'] = pd.to_datetime(sessions['session_start'])
orders['order_datetime'] = pd.to_datetime(orders['order_datetime'])
first_sessions = sessions.groupby('user_id')['session_start'].min().reset_index()
first_sessions.columns = ['user_id', 'first_session']
completed_orders = orders[orders['order_status'] == 'completed']
first_orders = completed_orders.groupby('user_id')['order_datetime'].min().reset_index()
first_orders.columns = ['user_id', 'first_order']

df = first_sessions.merge(first_orders, on='user_id')
df['diff_minutes'] = (df['first_order'] - df['first_session']).dt.total_seconds() / 60
df_filtered = df[df['diff_minutes'] <= 10080]

median_time = df_filtered['diff_minutes'].median()
print(f"Кол-во пользователей: {len(df_filtered)}")
print(f"Медианое время: {median_time} минут")