import pandas as pd    
import numpy as np                         
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('funnel_analysis_data.csv')
print(df.head())

print("\nCONVERTING TIMESTAMP TO DATETIME:")
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
print("This Convert to Timestamp to DateTime")
print(f"   Date range: {df['Timestamp'].min()} to {df['Timestamp'].max()}")

print("\nCREATING TIME-BASED FEATURES:")
# Extract time components
df['Hour'] = df['Timestamp'].dt.hour
df['DayOfWeek'] = df['Timestamp'].dt.day_name()
df['DayOfWeek_Num'] = df['Timestamp'].dt.dayofweek
df['Week'] = df['Timestamp'].dt.isocalendar().week
df['Month'] = df['Timestamp'].dt.month
df['Date'] = df['Timestamp'].dt.date

df['TimeOfDay'] = pd.cut(
    df['Hour'],
    bins=[0, 6, 12, 17, 20, 24],
    labels=['Night', 'Morning', 'Afternoon', 'Evening', 'Late Night'],
    right=False
)

print(f"Added columns:")
print(f"Hour: {df['Hour'].min()}-{df['Hour'].max()}")
print(f"DayOfWeek: {df['DayOfWeek'].unique().tolist()}")
print(f"Week: {df['Week'].min()} to {df['Week'].max()}")
print(f"TimeOfDay: {df['TimeOfDay'].unique().tolist()}")

print("\nCREATING SESSION-LEVEL DATA:")
print("-" * 50)

event_order = {'Browse': 1, 'Add to Cart': 2, 'Checkout': 3, 'Purchase': 4}
df['Event_Order'] = df['Event'].map(event_order)

session_max_event = df.groupby('Session_ID')['Event_Order'].max().reset_index()
session_max_event['Max_Event'] = session_max_event['Event_Order'].map({v: k for k, v in event_order.items()})

session_start = df.groupby('Session_ID')['Timestamp'].min().reset_index()
session_start.columns = ['Session_ID', 'Session_Start']

session_attrs = df.groupby('Session_ID').first().reset_index()[[
    'Session_ID', 'User_ID', 'Device', 'Region', 'Channel', 'Product_Category'
]]

session_df = session_attrs.merge(session_max_event, on='Session_ID')
session_df = session_df.merge(session_start, on='Session_ID')

print(f"Created session-level dataset with {len(session_df):,} sessions")
print(f"Columns: {list(session_df.columns)}")

browse_sessions = len(session_df)
cart_sessions = len(session_df[session_df['Max_Event'].isin(['Add to Cart', 'Checkout', 'Purchase'])])
checkout_sessions = len(session_df[session_df['Max_Event'].isin(['Checkout', 'Purchase'])])
purchase_sessions = len(session_df[session_df['Max_Event'] == 'Purchase'])

print(f"\n   STEP-BY-STEP CONVERSION:")
print(f"   Browse → Add to Cart:    {cart_sessions/browse_sessions*100:.1f}%")
print(f"   Add to Cart → Checkout:  {checkout_sessions/cart_sessions*100:.1f}%")
print(f"   Checkout → Purchase:     {purchase_sessions/checkout_sessions*100:.1f}%")

print("\nCONVERSION BY DEVICE:")
device_conversion = []
for device in session_df['Device'].unique():
    device_df = session_df[session_df['Device'] == device]
    total = len(device_df)
    purchases = len(device_df[device_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    device_conversion.append({
        'Device': device,
        'Sessions': total,
        'Purchases': purchases,
        'Conversion Rate %': round(conv_rate, 2)
    })
device_df_result = pd.DataFrame(device_conversion).sort_values('Conversion Rate %', ascending=False)
print(device_df_result.to_string(index=False))

print("\nCONVERSION BY REGION:")
region_conversion = []
for region in session_df['Region'].unique():
    region_df = session_df[session_df['Region'] == region]
    total = len(region_df)
    purchases = len(region_df[region_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    region_conversion.append({
        'Region': region,
        'Sessions': total,
        'Purchases': purchases,
        'Conversion Rate %': round(conv_rate, 2)
    })
region_df_result = pd.DataFrame(region_conversion).sort_values('Conversion Rate %', ascending=False)
print(region_df_result.to_string(index=False))

print("\nCONVERSION BY CHANNEL:")
channel_conversion = []
for channel in session_df['Channel'].unique():
    channel_df = session_df[session_df['Channel'] == channel]
    total = len(channel_df)
    purchases = len(channel_df[channel_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    channel_conversion.append({
        'Channel': channel,
        'Sessions': total,
        'Purchases': purchases,
        'Conversion Rate %': round(conv_rate, 2)
    })
channel_df_result = pd.DataFrame(channel_conversion).sort_values('Conversion Rate %', ascending=False)
print(channel_df_result.to_string(index=False))

print("\nCONVERSION BY PRODUCT CATEGORY:")
category_conversion = []
for category in session_df['Product_Category'].unique():
    category_df = session_df[session_df['Product_Category'] == category]
    total = len(category_df)
    purchases = len(category_df[category_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    category_conversion.append({
        'Product Category': category,
        'Sessions': total,
        'Purchases': purchases,
        'Conversion Rate %': round(conv_rate, 2)
    })
category_df_result = pd.DataFrame(category_conversion).sort_values('Conversion Rate %', ascending=False)
print(category_df_result.to_string(index=False))

print("\nCONVERSION BY TIME OF DAY:")
session_with_time = session_df.merge(
    df[['Session_ID', 'Hour', 'TimeOfDay', 'DayOfWeek']].drop_duplicates('Session_ID'),
    on='Session_ID'
)
time_conversion = []
for time_slot in session_with_time['TimeOfDay'].unique():
    time_df = session_with_time[session_with_time['TimeOfDay'] == time_slot]
    total = len(time_df)
    purchases = len(time_df[time_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100 if total > 0 else 0
    time_conversion.append({
        'Time of Day': time_slot,
        'Sessions': total,
        'Purchases': purchases,
        'Conversion Rate %': round(conv_rate, 2)
    })

time_df_result = pd.DataFrame(time_conversion).sort_values('Conversion Rate %', ascending=False)
print(time_df_result.to_string(index=False))

print("\nCONVERSION BY DAY OF WEEK:")

day_conversion = []
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

for day in day_order:
    day_df = session_with_time[session_with_time['DayOfWeek'] == day]
    total = len(day_df)
    purchases = len(day_df[day_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100 if total > 0 else 0
    day_conversion.append({
        'Day of Week': day,
        'Sessions': total,
        'Purchases': purchases,
        'Conversion Rate %': round(conv_rate, 2)
    })

day_df_result = pd.DataFrame(day_conversion)
print(day_df_result.to_string(index=False))

print("\nSAVING PREPARED DATA:")
import os
output_path = 'output'
os.makedirs(output_path, exist_ok=True)
session_df.to_csv(f"{output_path}/session_level_data.csv", index=False)
print(f"Saved session_level_data.csv ({len(session_df):,} rows)")
df.to_csv(f"{output_path}/full_data_with_features.csv", index=False)
print(f"Saved full_data_with_features.csv ({len(df):,} rows)")
conversion_summary = pd.DataFrame([
    {'Stage': 'Browse', 'Sessions': browse_sessions, 'Conversion %': 100.0},
    {'Stage': 'Add to Cart', 'Sessions': cart_sessions, 'Conversion %': round(cart_sessions/browse_sessions*100, 1)},
    {'Stage': 'Checkout', 'Sessions': checkout_sessions, 'Conversion %': round(checkout_sessions/browse_sessions*100, 1)},
    {'Stage': 'Purchase', 'Sessions': purchase_sessions, 'Conversion %': round(purchase_sessions/browse_sessions*100, 1)}
])

conversion_summary.to_csv(f"{output_path}/conversion_funnel_summary.csv", index=False)
print(f"Saved conversion_funnel_summary.csv")