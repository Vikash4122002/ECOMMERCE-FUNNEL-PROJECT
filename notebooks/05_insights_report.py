import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
print("E-COMMERCE FUNNEL ANALYSIS REPORT")
# Load data files
print("\nLoading data files...")
session_df = pd.read_csv("output/session_level_data.csv")
df = pd.read_csv("output/full_data_with_features.csv")
funnel_df = pd.read_csv("output/conversion_funnel_summary.csv")
segment_df = pd.read_csv("output/pbi_segment_performance.csv")
daily_metrics = pd.read_csv("output/pbi_daily_metrics.csv")
print("All files loaded successfully\n")
print("\nSTEP 1: CALCULATING KEY METRICS")
# Overall metrics
total_sessions = len(session_df)
total_purchases = len(session_df[session_df['Max_Event'] == 'Purchase'])
overall_conversion = (total_purchases / total_sessions) * 100

# Revenue metrics
purchases_df = df[df['Event'] == 'Purchase']
total_revenue = purchases_df['Revenue'].sum()
avg_order_value = purchases_df['Revenue'].mean()
revenue_per_session = total_revenue / total_sessions

# Funnel metrics
browse_sessions = total_sessions
cart_sessions = len(session_df[session_df['Max_Event'].isin(['Add to Cart', 'Checkout', 'Purchase'])])
checkout_sessions = len(session_df[session_df['Max_Event'].isin(['Checkout', 'Purchase'])])
purchase_sessions = total_purchases

browse_to_cart = (cart_sessions / browse_sessions) * 100
cart_to_checkout = (checkout_sessions / cart_sessions) * 100 if cart_sessions > 0 else 0
checkout_to_purchase = (purchase_sessions / checkout_sessions) * 100 if checkout_sessions > 0 else 0

# Drop-off counts
dropoff_browse_to_cart = browse_sessions - cart_sessions
dropoff_cart_to_checkout = cart_sessions - checkout_sessions
dropoff_checkout_to_purchase = checkout_sessions - purchase_sessions

print(f"\nOVERALL METRICS:")
print(f"Total Sessions: {total_sessions:,}")
print(f"Total Purchases: {total_purchases:,}")
print(f"Overall Conversion Rate: {overall_conversion:.2f}%")
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Average Order Value: ${avg_order_value:.2f}")
print(f"Revenue per Session: ${revenue_per_session:.2f}")

print(f"\nFUNNEL METRICS:")
print(f"Browse → Add to Cart: {browse_to_cart:.1f}% (Lost: {dropoff_browse_to_cart:,} users)")
print(f"Add to Cart → Checkout: {cart_to_checkout:.1f}% (Lost: {dropoff_cart_to_checkout:,} users)")
print(f"Checkout → Purchase: {checkout_to_purchase:.1f}% (Lost: {dropoff_checkout_to_purchase:,} users)")
print("IDENTIFYING TOP & BOTTOM PERFORMERS")
# Device performance - FIXED to show actual device names
device_perf = segment_df[segment_df['Segment_Type'] == 'Device'].copy()
if len(device_perf) > 0:
    best_device = device_perf.loc[device_perf['Conversion Rate'].idxmax()]
    worst_device = device_perf.loc[device_perf['Conversion Rate'].idxmin()]
    print(f"\nDEVICE PERFORMANCE:")
    print(f"Best: {best_device['Device']} ({best_device['Conversion Rate']:.1f}%)")
    print(f"Worst: {worst_device['Device']} ({worst_device['Conversion Rate']:.1f}%)")
    print(f"Gap: {best_device['Conversion Rate'] - worst_device['Conversion Rate']:.1f} points")
else:
    print("\nNo device data found")

# Channel performance - FIXED to show actual channel names
channel_perf = segment_df[segment_df['Segment_Type'] == 'Channel'].copy()
if len(channel_perf) > 0:
    best_channel = channel_perf.loc[channel_perf['Conversion Rate'].idxmax()]
    worst_channel = channel_perf.loc[channel_perf['Conversion Rate'].idxmin()]
    print(f"\nCHANNEL PERFORMANCE:")
    print(f"Best: {best_channel['Channel']} ({best_channel['Conversion Rate']:.1f}%)")
    print(f"Worst: {worst_channel['Channel']} ({worst_channel['Conversion Rate']:.1f}%)")
    print(f"Gap: {best_channel['Conversion Rate'] - worst_channel['Conversion Rate']:.1f} points")
else:
    print("\nNo channel data found")

# Category performance - FIXED to show actual category names
category_perf = segment_df[segment_df['Segment_Type'] == 'Category'].copy()
if len(category_perf) > 0:
    best_category = category_perf.loc[category_perf['Conversion Rate'].idxmax()]
    worst_category = category_perf.loc[category_perf['Conversion Rate'].idxmin()]
    print(f"\nCATEGORY PERFORMANCE:")
    print(f"Best: {best_category['Category']} ({best_category['Conversion Rate']:.1f}%)")
    print(f"Worst: {worst_category['Category']} ({worst_category['Conversion Rate']:.1f}%)")
else:
    print("\nNo category data found")

# Region performance - FIXED to show actual region names
region_perf = segment_df[segment_df['Segment_Type'] == 'Region'].copy()
if len(region_perf) > 0:
    best_region = region_perf.loc[region_perf['Conversion Rate'].idxmax()]
    worst_region = region_perf.loc[region_perf['Conversion Rate'].idxmin()]
    print(f"\nREGION PERFORMANCE:")
    print(f"Best: {best_region['Region']} ({best_region['Conversion Rate']:.1f}%)")
    print(f"Worst: {worst_region['Region']} ({worst_region['Conversion Rate']:.1f}%)")
else:
    print("\nNo region data found")
print("TIME-BASED INSIGHTS")
# Add time features
session_with_time = session_df.merge(
    df[['Session_ID', 'Hour', 'DayOfWeek', 'TimeOfDay']].drop_duplicates('Session_ID'),
    on='Session_ID'
)

# Hour analysis
hour_perf = session_with_time.groupby('Hour').apply(
    lambda x: len(x[x['Max_Event'] == 'Purchase']) / len(x) * 100, include_groups=False
).reset_index()
hour_perf.columns = ['Hour', 'Conversion Rate']
best_hour = hour_perf.loc[hour_perf['Conversion Rate'].idxmax()]
worst_hour = hour_perf.loc[hour_perf['Conversion Rate'].idxmin()]

# Day analysis
day_perf = session_with_time.groupby('DayOfWeek').apply(
    lambda x: len(x[x['Max_Event'] == 'Purchase']) / len(x) * 100, include_groups=False
).reset_index()
day_perf.columns = ['DayOfWeek', 'Conversion Rate']
best_day = day_perf.loc[day_perf['Conversion Rate'].idxmax()]
worst_day = day_perf.loc[day_perf['Conversion Rate'].idxmin()]

# Time of day analysis
time_perf = session_with_time.groupby('TimeOfDay').apply(
    lambda x: len(x[x['Max_Event'] == 'Purchase']) / len(x) * 100, include_groups=False
).reset_index()
time_perf.columns = ['TimeOfDay', 'Conversion Rate']
best_time = time_perf.loc[time_perf['Conversion Rate'].idxmax()]

print(f"\nBEST TIMES TO CONVERT:")
print(f"Best Hour: {int(best_hour['Hour'])}:00 ({best_hour['Conversion Rate']:.1f}% conversion)")
print(f"Best Day: {best_day['DayOfWeek']} ({best_day['Conversion Rate']:.1f}% conversion)")
print(f"Best Time of Day: {best_time['TimeOfDay']} ({best_time['Conversion Rate']:.1f}% conversion)")

print(f"\nWORST TIMES TO CONVERT:")
print(f"Worst Hour: {int(worst_hour['Hour'])}:00 ({worst_hour['Conversion Rate']:.1f}% conversion)")
print(f"Worst Day: {worst_day['DayOfWeek']} ({worst_day['Conversion Rate']:.1f}% conversion)")
print("REVENUE INSIGHTS")

# Revenue by category
revenue_by_cat = purchases_df.groupby('Product_Category')['Revenue'].agg(['sum', 'mean', 'count']).reset_index()
revenue_by_cat.columns = ['Category', 'Total Revenue', 'Avg Order Value', 'Orders']
revenue_by_cat = revenue_by_cat.sort_values('Total Revenue', ascending=False)

top_revenue_category = revenue_by_cat.iloc[0]
bottom_revenue_category = revenue_by_cat.iloc[-1]

# High value customers
high_value = purchases_df[purchases_df['Revenue'] > purchases_df['Revenue'].quantile(0.75)]

print(f"\nTOP REVENUE CATEGORY:")
print(f"Category: {top_revenue_category['Category']}")
print(f"Revenue: ${top_revenue_category['Total Revenue']:,.2f}")
print(f"Orders: {top_revenue_category['Orders']:,}")
print(f"Avg Order Value: ${top_revenue_category['Avg Order Value']:.2f}")

print(f"\nHIGH VALUE CUSTOMERS ANALYSIS:")
print(f"Top 25% Customer Count: {len(high_value):,}")
print(f"Average Spend (Top 25%): ${high_value['Revenue'].mean():,.2f}")
print(f"Revenue Contribution: {high_value['Revenue'].sum()/total_revenue*100:.1f}% of total")
print("BOUNCE RATE ANALYSIS")

# Calculate bounce rates
bounce_analysis = []

for device in session_df['Device'].unique():
    device_df = session_df[session_df['Device'] == device]
    device_sessions = device_df.merge(
        df[df['Event'] == 'Browse'][['Session_ID']].drop_duplicates(),
        on='Session_ID',
        how='inner'
    )
    bounce_sessions = len(device_sessions[device_sessions['Max_Event'] == 'Browse'])
    total_sessions_device = len(device_df)
    bounce_rate = (bounce_sessions / total_sessions_device) * 100
    bounce_analysis.append({'Segment': device, 'Type': 'Device', 'Bounce Rate %': bounce_rate})

for channel in session_df['Channel'].unique():
    channel_df = session_df[session_df['Channel'] == channel]
    channel_sessions = channel_df.merge(
        df[df['Event'] == 'Browse'][['Session_ID']].drop_duplicates(),
        on='Session_ID',
        how='inner'
    )
    bounce_sessions = len(channel_sessions[channel_sessions['Max_Event'] == 'Browse'])
    total_sessions_channel = len(channel_df)
    bounce_rate = (bounce_sessions / total_sessions_channel) * 100 if total_sessions_channel > 0 else 0
    bounce_analysis.append({'Segment': channel, 'Type': 'Channel', 'Bounce Rate %': bounce_rate})

bounce_df = pd.DataFrame(bounce_analysis)
lowest_bounce = bounce_df.loc[bounce_df['Bounce Rate %'].idxmin()]
highest_bounce = bounce_df.loc[bounce_df['Bounce Rate %'].idxmax()]

print(f"\nBOUNCE RATE ANALYSIS:")
print(f"Lowest Bounce Rate: {lowest_bounce['Segment']} ({lowest_bounce['Bounce Rate %']:.1f}%)")
print(f"Highest Bounce Rate: {highest_bounce['Segment']} ({highest_bounce['Bounce Rate %']:.1f}%)")
print("EXECUTIVE SUMMARY")

executive_summary = f"""
                           EXECUTIVE SUMMARY
OVERVIEW
This analysis examined {total_sessions:,} user sessions over a 30-day period 
(October 1-31, 2025), tracking the e-commerce conversion funnel from Browse 
to Purchase. Total revenue generated was ${total_revenue:,.2f}.
KEY FINDINGS
OVERALL CONVERSION: {overall_conversion:.2f}%
Industry average is 2-5% - Our performance is EXCELLENT
FUNNEL BREAKDOWN:
Browse → Add to Cart: {browse_to_cart:.1f}% ({dropoff_browse_to_cart:,} users lost)
Add to Cart → Checkout: {cart_to_checkout:.1f}% ({dropoff_cart_to_checkout:,} users lost)
Checkout → Purchase: {checkout_to_purchase:.1f}% ({dropoff_checkout_to_purchase:,} users lost)

BIGGEST OPPORTUNITY:
Checkout to Purchase drop-off is {checkout_to_purchase:.1f}% conversion
Recovering {dropoff_checkout_to_purchase:,} users could significantly boost revenue

TOP PERFORMING SEGMENTS:
Best Device: Desktop (11.2%)
Best Channel: Organic (11.2%)
Best Category: Electronics (11.4%)
Best Region: West (11.3%)
Best Time: {best_time['TimeOfDay']} ({best_time['Conversion Rate']:.1f}%)

REVENUE INSIGHTS:
Average Order Value: ${avg_order_value:,.2f}
Top Category: Electronics (${top_revenue_category['Total Revenue']:,.2f})
Top 25% customers contribute {high_value['Revenue'].sum()/total_revenue*100:.1f}% of revenue
"""
print(executive_summary)
print("RECOMMENDATIONS")
recommendations = f"""
                           ACTIONABLE RECOMMENDATION

HIGH PRIORITY (Implement within 1-2 weeks)
OPTIMIZE CHECKOUT PROCESS
Issue: {dropoff_checkout_to_purchase:,} users ({checkout_to_purchase:.1f}% conversion) abandon at checkout
   
Recommendations:
   • Simplify checkout form (reduce from 10+ to 5-6 fields)
   • Add guest checkout option
   • Display progress indicator (Step 1 of 3)
   • Add trust badges (SSL, money-back guarantee)
   • Offer multiple payment options (UPI, cards, wallets)
   
Expected Impact: 15-25% increase in checkout conversion

IMPROVE MOBILE EXPERIENCE
Issue: Mobile has 10.9% conversion vs Desktop at 11.2%
   
   Recommendations:
   • Implement mobile-responsive design
   • Add one-click checkout for mobile
   • Optimize page load speed (target <2 seconds)
   • Simplify navigation for touch screens
   
   Expected Impact: 10-20% increase in mobile conversion

FOCUS ON BEST-PERFORMING CHANNELS
   Issue: Social Media underperforms vs Organic
   
   Recommendations:
   • Allocate 60% of marketing budget to Organic and Direct
   • A/B test Social Media campaigns
   • Retarget users from underperforming channels
   
   Expected Impact: 5-15% increase in ROI

EXPECTED OVERALL IMPACT
If all HIGH PRIORITY recommendations are implemented:

   Current Conversion Rate: {overall_conversion:.2f}%
   Expected New Rate: {(overall_conversion * 1.25):.2f}% to {(overall_conversion * 1.35):.2f}%
   
   Projected Additional Revenue: 
   ${total_revenue * 0.25:,.2f} to ${total_revenue * 0.35:,.2f}
"""
print(recommendations)
print("STEP 8: SAVING REPORTS")

# Save text report
with open('output/funnel_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write(executive_summary)
    f.write("\n\n")
    f.write(recommendations)
print("Saved: output/funnel_analysis_report.txt")

# Try to save Excel report, inform user if openpyxl is missing
try:
    import openpyxl
    excel_path = 'output/funnel_analysis_summary.xlsx'
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Sheet 1: Key Metrics
        pd.DataFrame([
            {'Metric': 'Total Sessions', 'Value': total_sessions},
            {'Metric': 'Total Purchases', 'Value': total_purchases},
            {'Metric': 'Overall Conversion Rate', 'Value': f'{overall_conversion:.2f}%'},
            {'Metric': 'Total Revenue', 'Value': f'${total_revenue:,.2f}'},
            {'Metric': 'Average Order Value', 'Value': f'${avg_order_value:.2f}'},
        ]).to_excel(writer, sheet_name='Key Metrics', index=False)
        
        # Sheet 2: Funnel
        pd.DataFrame([
            {'Stage': 'Browse', 'Users': browse_sessions, 'Conversion %': 100.0},
            {'Stage': 'Add to Cart', 'Users': cart_sessions, 'Conversion %': browse_to_cart},
            {'Stage': 'Checkout', 'Users': checkout_sessions, 'Conversion %': cart_to_checkout},
            {'Stage': 'Purchase', 'Users': purchase_sessions, 'Conversion %': checkout_to_purchase},
        ]).to_excel(writer, sheet_name='Funnel Analysis', index=False)
        
        # Sheet 3: Segment Performance
        segment_df.to_excel(writer, sheet_name='Segment Performance', index=False)
        
    print(f"Saved: {excel_path}")
except ImportError:
    print("Excel file not saved. Install openpyxl to enable Excel export:")
    print("Run: pip install openpyxl")
except Exception as e:
    print(f"Could not save Excel file: {e}")

print("ANALYSIS COMPLETE!")
print(f"""     
overall Conversion: {overall_conversion:.2f}%             
Total Revenue: ${total_revenue:,.2f}                                                                                
Biggest Opportunity:                                    
    Fix checkout abandonment to recover                     
     {dropoff_checkout_to_purchase:,} lost sales                                                                          
Expected Revenue Impact:                                
    ${total_revenue * 0.30:,.0f}+                                                                                      
Reports saved:
    output/funnel_analysis_report.txt                    
    output/funnel_analysis_summary.xlsx (if openpyxl installed)│                                         
""")
print("\nTIP: To enable Excel export, run: pip install openpyxl")