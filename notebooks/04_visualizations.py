import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Load session-level data from Step 3
session_df = pd.read_csv('output/session_level_data.csv')
df = pd.read_csv('output/full_data_with_features.csv')

df['Timestamp'] = pd.to_datetime(df['Timestamp'])

print("\nCREATING FUNNEL CHART...")
# Calculate funnel stages
funnel_data = {
    'Stage': ['Browse', 'Add to Cart', 'Checkout', 'Purchase'],
    'Users': [
        len(session_df),
        len(session_df[session_df['Max_Event'].isin(['Add to Cart', 'Checkout', 'Purchase'])]),
        len(session_df[session_df['Max_Event'].isin(['Checkout', 'Purchase'])]),
        len(session_df[session_df['Max_Event'] == 'Purchase'])
    ]
}
funnel_df = pd.DataFrame(funnel_data)
funnel_df['Conversion Rate'] = (funnel_df['Users'] / funnel_df['Users'].iloc[0]) * 100
funnel_df['Drop-off'] = funnel_df['Users'].diff().fillna(0).abs()
funnel_df['Drop-off'][0] = 0
# Funnel Chart (Left)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
bars = axes[0].barh(funnel_df['Stage'], funnel_df['Users'], color=colors, edgecolor='white', linewidth=2)
# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, funnel_df['Users'])):
    axes[0].text(val + 100, bar.get_y() + bar.get_height()/2, f'{val:,}',
                  
                 va='center', fontsize=11, fontweight='bold')

axes[0].set_xlabel('Number of Users', fontsize=12)
axes[0].set_title('E-Commerce Conversion Funnel', fontsize=14, fontweight='bold')
axes[0].invert_yaxis()

# Conversion Rate Chart (Right)
bars2 = axes[1].bar(funnel_df['Stage'], funnel_df['Conversion Rate'], color=colors, edgecolor='white', linewidth=2)


for bar, val in zip(bars2, funnel_df['Conversion Rate']):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.1f}%', 
                 ha='center', va='bottom', fontsize=11, fontweight='bold')

axes[1].set_ylabel('Conversion Rate (%)', fontsize=12)
axes[1].set_title('Conversion Rates by Stage', fontsize=14, fontweight='bold')
axes[1].set_ylim(0, 105)

import os

output_path = 'output'
os.makedirs(output_path, exist_ok=True)
plt.tight_layout()
plt.savefig(f"{output_path}/funnel_chart.png", dpi=150, bbox_inches='tight')
plt.show()
print("Saved:", os.path.abspath(f"{output_path}/funnel_chart.png"))

print("\nCREATING DROP-OFF ANALYSIS CHART...")
stages = ['Browse → Cart', 'Cart → Checkout', 'Checkout → Purchase']

dropoff_counts = [
    funnel_df['Users'].iloc[0] - funnel_df['Users'].iloc[1],
    funnel_df['Users'].iloc[1] - funnel_df['Users'].iloc[2],
    funnel_df['Users'].iloc[2] - funnel_df['Users'].iloc[3]
]
dropoff_percentages = [
    (dropoff_counts[0] / funnel_df['Users'].iloc[0]) * 100,
    (dropoff_counts[1] / funnel_df['Users'].iloc[1]) * 100,
    (dropoff_counts[2] / funnel_df['Users'].iloc[2]) * 100
]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Drop-off counts
colors_drop = ['#e74c3c', '#e67e22', '#f39c12']
bars1 = ax1.bar(stages, dropoff_counts, color=colors_drop, edgecolor='white', linewidth=2)
for bar, val in zip(bars1, dropoff_counts):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, f'{val:,}', 
             ha='center', va='bottom', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Users Lost', fontsize=12)
ax1.set_title('Users Lost at Each Stage', fontsize=14, fontweight='bold')

# Drop-off percentages
bars2 = ax2.bar(stages, dropoff_percentages, color=colors_drop, edgecolor='white', linewidth=2)
for bar, val in zip(bars2, dropoff_percentages):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,f'{val:.1f}%', ha='center',va='bottom',fontsize=11,fontweight='bold')
ax2.set_ylabel('Drop-off Rate (%)', fontsize=12)
ax2.set_title('Drop-off Rates at Each Stage', fontsize=14, fontweight='bold')
ax2.set_ylim(0, max(dropoff_percentages) + 10)
import os
os.makedirs('output', exist_ok=True)
plt.tight_layout()
plt.savefig('output/dropoff_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: dropoff_analysis.png")

print("\nCREATING DEVICE CONVERSION CHART...")
device_conversion = []
for device in session_df['Device'].unique():
    device_df = session_df[session_df['Device'] == device]
    total = len(device_df)
    purchases = len(device_df[device_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    device_conversion.append({'Device': device, 'Conversion Rate': conv_rate, 'Sessions': total})

device_df_plot = pd.DataFrame(device_conversion)
fig, ax = plt.subplots(figsize=(10, 6))
colors_dev = ['#3498db', '#2ecc71', '#e74c3c']
bars = ax.bar(device_df_plot['Device'], device_df_plot['Conversion Rate'], color=colors_dev, edgecolor='white', linewidth=2)

for bar, val in zip(bars, device_df_plot['Conversion Rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f'{val:.1f}%', 
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_xlabel('Device Type', fontsize=12)
ax.set_ylabel('Conversion Rate (%)', fontsize=12)
ax.set_title('Conversion Rate by Device', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(device_df_plot['Conversion Rate']) + 5)
import os

# Create output folder inside project
os.makedirs('output', exist_ok=True)

plt.tight_layout()
plt.savefig('output/conversion_by_device.png', dpi=150, bbox_inches='tight')
plt.show()

print("Saved: conversion_by_device.png")
print("\nCREATING CHANNEL CONVERSION CHART...")
channel_conversion = []
for channel in session_df['Channel'].unique():
    channel_df = session_df[session_df['Channel'] == channel]
    total = len(channel_df)
    purchases = len(channel_df[channel_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    channel_conversion.append({'Channel': channel, 'Conversion Rate': conv_rate, 'Sessions': total})
channel_df_plot = pd.DataFrame(channel_conversion).sort_values('Conversion Rate', ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))
colors_chan = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
bars = ax.bar(channel_df_plot['Channel'], channel_df_plot['Conversion Rate'], color=colors_chan, edgecolor='white', linewidth=2)
for bar, val in zip(bars, channel_df_plot['Conversion Rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f'{val:.1f}%', 
            ha='center', va='bottom', fontsize=12, fontweight='bold')
ax.set_xlabel('Acquisition Channel', fontsize=12)
ax.set_ylabel('Conversion Rate (%)', fontsize=12)
ax.set_title('Conversion Rate by Channel', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(channel_df_plot['Conversion Rate']) + 5)
import os
os.makedirs('output', exist_ok=True)
plt.tight_layout()
plt.savefig('output/conversion_by_channel.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: conversion_by_channel.png")

print("\nCREATING PRODUCT CATEGORY CONVERSION CHART...")
category_conversion = []
for category in session_df['Product_Category'].unique():
    category_df = session_df[session_df['Product_Category'] == category]
    total = len(category_df)
    purchases = len(category_df[category_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    category_conversion.append({'Category': category, 'Conversion Rate': conv_rate, 'Sessions': total})
category_df_plot = pd.DataFrame(category_conversion).sort_values('Conversion Rate', ascending=False)
fig, ax = plt.subplots(figsize=(12, 6))
colors_cat = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']
bars = ax.bar(category_df_plot['Category'], category_df_plot['Conversion Rate'], color=colors_cat, edgecolor='white', linewidth=2)
for bar, val in zip(bars, category_df_plot['Conversion Rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f'{val:.1f}%', 
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xlabel('Product Category', fontsize=12)
ax.set_ylabel('Conversion Rate (%)', fontsize=12)
ax.set_title('Conversion Rate by Product Category', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(category_df_plot['Conversion Rate']) + 5)
plt.xticks(rotation=45, ha='right')
import os
# Create output folder inside project
os.makedirs('output', exist_ok=True)

plt.tight_layout()
plt.savefig('output/conversion_by_category.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: conversion_by_category.png")

print("\nCREATING REGION CONVERSION CHART...")
region_conversion = []
for region in session_df['Region'].unique():
    region_df = session_df[session_df['Region'] == region]
    total = len(region_df)
    purchases = len(region_df[region_df['Max_Event'] == 'Purchase'])
    conv_rate = purchases / total * 100
    region_conversion.append({'Region': region, 'Conversion Rate': conv_rate, 'Sessions': total})
region_df_plot = pd.DataFrame(region_conversion).sort_values('Conversion Rate', ascending=True)
fig, ax = plt.subplots(figsize=(10, 6))
colors_reg = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
bars = ax.barh(region_df_plot['Region'], region_df_plot['Conversion Rate'], color=colors_reg, edgecolor='white', linewidth=2)
for bar, val in zip(bars, region_df_plot['Conversion Rate']):
    ax.text(val + 0.2, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
            va='center', fontsize=11, fontweight='bold')
ax.set_xlabel('Conversion Rate (%)', fontsize=12)
ax.set_ylabel('Region', fontsize=12)
ax.set_title('Conversion Rate by Region', fontsize=14, fontweight='bold')
import os
os.makedirs('output', exist_ok=True)
plt.tight_layout()
plt.savefig('output/conversion_by_region.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: conversion_by_region.png")

print("\nCREATING HEATMAP (Hour vs Day)...")
# Prepare data for heatmap
session_with_time = session_df.merge(
    df[['Session_ID', 'Hour', 'DayOfWeek', 'DayOfWeek_Num']].drop_duplicates('Session_ID'), 
    on='Session_ID'
)
# Create pivot table for conversion rates
heatmap_data = []
for hour in range(24):
    for day_num, day_name in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):

        subset = session_with_time[
            (session_with_time['Hour'] == hour) & 
            (session_with_time['DayOfWeek'] == day_name)
        ]
        total = len(subset)
        purchases = len(subset[subset['Max_Event'] == 'Purchase'])
        conv_rate = (purchases / total * 100) if total > 0 else 0
        heatmap_data.append({'Hour': hour, 'Day': day_name, 'Day_Num': day_num, 'Conversion Rate': conv_rate})
heatmap_df = pd.DataFrame(heatmap_data)
heatmap_pivot = heatmap_df.pivot(index='Hour', columns='Day', values='Conversion Rate')
heatmap_pivot = heatmap_pivot[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]

# Create heatmap
fig, ax = plt.subplots(figsize=(14, 10))
im = ax.imshow(heatmap_pivot.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=20)

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Conversion Rate (%)', fontsize=12)
#set labels
ax.set_xticks(range(len(heatmap_pivot.columns)))
ax.set_xticklabels(heatmap_pivot.columns, fontsize=11)
ax.set_yticks(range(len(heatmap_pivot.index)))
ax.set_yticklabels(heatmap_pivot.index, fontsize=11)
ax.set_xlabel('Day of Week', fontsize=12)
ax.set_ylabel('Hour of Day', fontsize=12)
ax.set_title('Conversion Rate Heatmap: Hour vs Day', fontsize=14, fontweight='bold')
for i in range(len(heatmap_pivot.index)):
    for j in range(len(heatmap_pivot.columns)):
        value = heatmap_pivot.values[i, j]
        if not np.isnan(value):
            text_color = 'white' if value < 10 else 'black'
            ax.text(j, i, f'{value:.1f}%', ha='center', va='center', 
                   fontsize=9, color=text_color, fontweight='bold')
import os

# Create output folder inside project
os.makedirs('output', exist_ok=True)

plt.tight_layout()
plt.savefig('output/conversion_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()

print("Saved: conversion_heatmap.png")
print("CREATING REVENUE BY CATEGORY CHART...")
# Get purchase data
purchases_df = df[df['Event'] == 'Purchase'].copy()
# Revenue by category
revenue_by_category = purchases_df.groupby('Product_Category')['Revenue'].agg(['sum', 'count', 'mean']).reset_index()
revenue_by_category.columns = ['Category', 'Total Revenue', 'Orders', 'Avg Order Value']
revenue_by_category = revenue_by_category.sort_values('Total Revenue', ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
# Total Revenue by Category
colors_rev = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']
bars1 = ax1.bar(revenue_by_category['Category'], revenue_by_category['Total Revenue'], color=colors_rev, edgecolor='white', linewidth=2)
for bar, val in zip(bars1, revenue_by_category['Total Revenue']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000, f'${val:,.0f}', 
             ha='center', va='bottom', fontsize=10, fontweight='bold', rotation=0)
ax1.set_xlabel('Product Category', fontsize=12)
ax1.set_ylabel('Total Revenue ($)', fontsize=12)
ax1.set_title('Total Revenue by Category', fontsize=14, fontweight='bold')
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
# Orders by Category
bars2 = ax2.bar(revenue_by_category['Category'], revenue_by_category['Orders'], color=colors_rev, edgecolor='white', linewidth=2)
for bar, val in zip(bars2, revenue_by_category['Orders']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, f'{val:,}', 
             ha='center', va='bottom', fontsize=11, fontweight='bold')
ax2.set_xlabel('Product Category', fontsize=12)
ax2.set_ylabel('Number of Orders', fontsize=12)
ax2.set_title('Orders by Category', fontsize=14, fontweight='bold')
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
import os
# Create output folder inside project
os.makedirs('output', exist_ok=True)
plt.tight_layout()
plt.savefig('output/revenue_by_category.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: revenue_by_category.png")

print("CREATING AVERAGE ORDER VALUE CHART...")
fig, ax = plt.subplots(figsize=(12, 6))
colors_aov = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']
bars = ax.bar(revenue_by_category['Category'], revenue_by_category['Avg Order Value'], color=colors_aov, edgecolor='white', linewidth=2)
for bar, val in zip(bars, revenue_by_category['Avg Order Value']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, f'${val:,.0f}', 
            ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.set_xlabel('Product Category', fontsize=12)
ax.set_ylabel('Average Order Value ($)', fontsize=12)
ax.set_title('Average Order Value by Category', fontsize=14, fontweight='bold')
ax.axhline(y=revenue_by_category['Avg Order Value'].mean(), color='red', linestyle='--', 
           linewidth=2, label=f"Overall Average: ${revenue_by_category['Avg Order Value'].mean():,.0f}")
ax.legend()
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
import os

# Create output folder inside project
os.makedirs('output', exist_ok=True)

plt.tight_layout()
plt.savefig('output/avg_order_value_by_category.png', dpi=150, bbox_inches='tight')
plt.show()

print("Saved: avg_order_value_by_category.png")

print("\nCREATING DAILY REVENUE TREND...")
# Daily revenue
purchases_df['Date'] = purchases_df['Timestamp'].dt.date
daily_revenue = purchases_df.groupby('Date')['Revenue'].agg(['sum', 'count']).reset_index()
daily_revenue.columns = ['Date', 'Revenue', 'Orders']

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Daily Revenue
ax1.plot(daily_revenue['Date'], daily_revenue['Revenue'], marker='o', linewidth=2, markersize=6, color='#2ecc71')
ax1.fill_between(daily_revenue['Date'], daily_revenue['Revenue'], alpha=0.3, color='#2ecc71')
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Daily Revenue ($)', fontsize=12)
ax1.set_title('Daily Revenue Trend', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
# Daily Orders
ax2.bar(daily_revenue['Date'], daily_revenue['Orders'], color='#3498db', edgecolor='white', linewidth=1)
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Number of Orders', fontsize=12)
ax2.set_title('Daily Orders Trend', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
import os

# Create output folder inside project
os.makedirs('output', exist_ok=True)

plt.tight_layout()
plt.savefig('output/daily_revenue_trend.png', dpi=150, bbox_inches='tight')
plt.show()

print("Saved: daily_revenue_trend.png")\


import os

print("\nEXPORTING DATA FOR POWER BI DASHBOARD...")

# Create output folder inside project
os.makedirs('output', exist_ok=True)

# Export session data for Power BI
session_df.to_csv('output/pbi_session_data.csv', index=False)
print("Saved: pbi_session_data.csv")

# Export funnel summary
funnel_summary = pd.DataFrame({
    'Stage': ['Browse', 'Add to Cart', 'Checkout', 'Purchase'],
    'Users': funnel_df['Users'],
    'Conversion Rate %': funnel_df['Conversion Rate']
})

funnel_summary.to_csv('output/pbi_funnel_summary.csv', index=False)
print("aved: pbi_funnel_summary.csv")
import os

# Create output folder inside project
os.makedirs('output', exist_ok=True)

# Export segment performance
segment_performance = pd.concat([
    device_df_plot.assign(Segment_Type='Device'),
    channel_df_plot.assign(Segment_Type='Channel'),
    category_df_plot.assign(Segment_Type='Product Category'),
    region_df_plot.assign(Segment_Type='Region')
])

segment_performance.to_csv('output/pbi_segment_performance.csv', index=False)
print("Saved: pbi_segment_performance.csv")

import os

# Create output folder inside project
os.makedirs('output', exist_ok=True)

# Export daily metrics
daily_metrics = df[df['Event'] == 'Purchase'].groupby(df['Timestamp'].dt.date).agg(
    Date=('Timestamp', 'first'),
    Revenue=('Revenue', 'sum'),
    Orders=('Event', 'count'),
    Avg_Order_Value=('Revenue', 'mean')
).reset_index(drop=True)

daily_metrics.to_csv('output/pbi_daily_metrics.csv', index=False)
print("Saved: pbi_daily_metrics.csv")

print("\nAll data exported for Power BI dashboard!")


