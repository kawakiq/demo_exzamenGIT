import pandas as pd
df = pd.read_csv('Sessions_analytics.csv')
df['session_start'] = pd.to_datetime(df['session_start'])

first_sessions = df.sort_values('session_start').drop_duplicates(subset=['user_id'], keep='first')
jan_users = first_sessions[
    (first_sessions['session_start'].dt.year == 2026) &
    (first_sessions['session_start'].dt.month == 1)
].copy()
jan_user_ids = jan_users['user_id'].tolist()


feb_sessions = df[
    (df['user_id'].isin(jan_user_ids)) &
    (df['session_start'].dt.year == 2026) &
    (df['session_start'].dt.month == 2)
]
returned_user_ids = feb_sessions['user_id'].unique()
jan_users['returned'] = jan_users['user_id'].isin(returned_user_ids)

retention_by_channel = jan_users.groupby('traffic_source')['returned'].mean()
best_channel = retention_by_channel.idxmax()
max_retention = retention_by_channel.max()
print("Удержание по каналам:")
print(retention_by_channel.sort_values(ascending=False).apply(lambda x: f"{x:.1%}"))
print(f"\nКанал с максимальным удержанием: {best_channel.upper()} ({max_retention:.1%})")