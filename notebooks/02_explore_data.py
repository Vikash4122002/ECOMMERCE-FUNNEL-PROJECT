import pandas as pd
import numpy as np
df = pd.read_csv("funnel_analysis_data.csv")
print(df.head())
print("\n BASIC INFORMATION:")
print(f"Total rows (events): {df.shape[0]:,}")
print(f"Total columns: {df.shape[1]}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
column_info = pd.DataFrame({
    'Column Name': df.columns,
    'Data Type': df.dtypes.values,
    'Unique Values': [df[col].nunique() for col in df.columns],
    'Missing Values': [df[col].isnull().sum() for col in df.columns],
    'Sample Value': [str(df[col].iloc[0]) if not df[col].empty else "N/A" for col in df.columns]
})
print(column_info.to_string(index=False))
print(df.head(10).to_string())
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct.round(2)
})
print(missing_df[missing_df['Missing Count'] > 0])
if missing.sum() == 0:
    print("EXCELLENT: No missing values found in any column!")
# Duplicate check
print("\nDuplicate Value")
print(f"Duplicates Row : {df.duplicated().sum():,}")
print(f"Drop Rows : {df.drop_duplicates().shape[0]:,}")
# Users & sessions
print("\nUSERS & SESSIONS:")
print(f"Unique Users: {df['User_ID'].nunique():,}")
print(f"Unique Sessions: {df['Session_ID'].nunique():,}")
print(f"Avg events per session: {df.shape[0] / df['Session_ID'].nunique():.2f}")
# Event distribution
print("\nEVENT DISTRIBUTION (FUNNEL STAGES):")
df['Event'] = df['Event'].str.strip()
event_counts = df['Event'].value_counts()
event_pct = (event_counts / len(df)) * 100
for event, count in event_counts.items():
    print(f"   {event:12} : {count:5,} ({event_pct[event]:5.1f}%)")
# Purchase Analysis
purchases = df[df['Event'] == 'Purchase'].copy()
print(f"\nTotal Purchases: {len(purchases):,}")
print(f"Total Revenue: {purchases['Revenue'].sum():,.2f}")
print(f"Average Order Value: {purchases['Revenue'].mean():,.2f}")
print(f"Min Order: {purchases['Revenue'].min():,.2f}")
print(f"Max Order: {purchases['Revenue'].max():,.2f}")
print("\n REVENUE DISTRIBUTION:")

revenue_bins = [0, 100, 250, 500, 1000, float('inf')]
revenue_labels = ['0-100', '100-250', '250-500', '500-1000', '1000+']
purchases['Revenue_Range'] = pd.cut(
    purchases['Revenue'],
    bins=revenue_bins,
    labels=revenue_labels,
    right=False
)
revenue_dist = purchases['Revenue_Range'].value_counts()
for range_name, count in revenue_dist.items():
    print(f"   {range_name:12} : {count:3} orders ({count/len(purchases)*100:.1f}%)")
print("\nDEVICE DISTRIBUTION:")
device_counts = df['Device'].value_counts()
device_pct = (device_counts / len(df)) * 100
for device, count in device_counts.items():
    print(f"   {device:10} : {count:5,} ({device_pct[device]:5.1f}%)")
# Region distribution
print("\nREGION DISTRIBUTION:")
region_counts = df['Region'].value_counts()
region_pct = (region_counts / len(df)) * 100
for region, count in region_counts.items():
    print(f"   {region:8} : {count:5,} ({region_pct[region]:5.1f}%)")
# Channel distribution
print("\nCHANNEL DISTRIBUTION:")
channel_counts = df['Channel'].value_counts()
channel_pct = (channel_counts / len(df)) * 100
for channel, count in channel_counts.items():
    print(f"   {channel:14} : {count:5,} ({channel_pct[channel]:5.1f}%)")
# Product category
print("\nPRODUCT CATEGORY DISTRIBUTION:")
category_counts = df['Product_Category'].value_counts()
category_pct = (category_counts / len(df)) * 100
for category, count in category_counts.items():
    print(f"   {category:14} : {count:5,} ({category_pct[category]:5.1f}%)")
# Bounce analysis
print("\nBOUNCE FLAG ANALYSIS:")
bounce_counts = df['Bounce_Flag'].value_counts()
unique_sessions = df.groupby('Session_ID')['Event'].nunique()
bounce_sessions = unique_sessions[unique_sessions == 1].count()
total_sessions = df['Session_ID'].nunique()
print(f"Bounce Flag - Yes: {bounce_counts.get('Yes', 0):,} events")
print(f"Bounce Flag - No: {bounce_counts.get('No', 0):,} events")
print(f"\nSessions with only 1 event (True Bounces): {bounce_sessions:,}")
print(f"Total Sessions: {total_sessions:,}")
print(f"True Bounce Rate: {bounce_sessions/total_sessions*100:.1f}%")
# Time analysis
print("\nTIME ANALYSIS:")
if 'Timestamp' in df.columns:
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    print(f"Date range: {df['Timestamp'].min().date()} to {df['Timestamp'].max().date()}")
    print(f"Total days: {(df['Timestamp'].max() - df['Timestamp'].min()).days + 1}")
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.day_name()
    df['Date'] = df['Timestamp'].dt.date
    print("\nBUSIEST HOURS:")
    hour_counts = df['Hour'].value_counts().head(5)
    for hour, count in hour_counts.items():
        print(f"   {hour:02d}:00 - {count:4,} events")
    print("\nBUSIEST DAYS:")
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day_counts = df['DayOfWeek'].value_counts()
    for day in day_order:
        if day in day_counts:
            print(f"   {day:9} : {day_counts[day]:4,} events")
# Funnel conversion
print("\nFUNNEL CONVERSION RATES (Overall):")
browse_sessions = df[df['Event'] == 'Browse']['Session_ID'].nunique()
cart_sessions = df[df['Event'] == 'Add to Cart']['Session_ID'].nunique()
checkout_sessions = df[df['Event'] == 'Checkout']['Session_ID'].nunique()
purchase_sessions = df[df['Event'] == 'Purchase']['Session_ID'].nunique()
print(f"   Browse → {browse_sessions:,} sessions")
print(f"   Add to Cart → {cart_sessions:,} sessions ({cart_sessions/browse_sessions*100:.1f}%)")
print(f"   Checkout → {checkout_sessions:,} sessions ({checkout_sessions/browse_sessions*100:.1f}%)")
print(f"   Purchase → {purchase_sessions:,} sessions ({purchase_sessions/browse_sessions*100:.1f}%)")
print(f"\nOverall Conversion Rate (Browse → Purchase): {purchase_sessions/browse_sessions*100:.2f}%")