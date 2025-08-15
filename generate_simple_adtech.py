#!/usr/bin/env python3
"""
Generate simplified AdTech demo data with storytelling focus
- campaigns (50 records)
- publishers (25 records) 
- ad_events (500K records)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_campaigns(num_campaigns=50):
    """Generate campaigns dimension with storytelling focus"""
    print(f"🏗️ Generating {num_campaigns} campaigns...")
    
    # Realistic advertisers and campaigns
    advertisers = {
        'AutoCorp': ['EV_Launch_2024', 'Summer_Sales', 'Holiday_Promo'],
        'TechInc': ['AI_Product_Launch', 'Mobile_App_Install', 'B2B_Lead_Gen'],
        'FinanceFirst': ['Credit_Card_Signup', 'Investment_App', 'Insurance_Awareness'],
        'RetailGiant': ['Back_to_School', 'Black_Friday', 'Spring_Collection'],
        'HealthPlus': ['Wellness_App', 'Telemedicine', 'Fitness_Tracker']
    }
    
    industries = ['automotive', 'tech', 'finance', 'retail', 'healthcare']
    campaign_types = ['display', 'video', 'search']
    devices = ['mobile', 'desktop', 'all']
    statuses = ['active', 'paused', 'completed']
    
    campaigns = []
    campaign_id = 1
    
    for advertiser, campaign_list in advertisers.items():
        industry = industries[list(advertisers.keys()).index(advertiser)]
        
        for campaign_base in campaign_list:
            # Create multiple variants (different types/devices)
            for campaign_type in random.sample(campaign_types, 2):  # 2 types per base campaign
                campaign_name = f"{advertiser}_{campaign_base}_{campaign_type}"
                
                # Generate realistic campaign start dates across 2022-2024
                year = random.choice([2022, 2023, 2024])
                if year == 2022:
                    start_month = random.randint(1, 12)
                elif year == 2023:
                    start_month = random.randint(1, 12)
                else:  # 2024
                    start_month = random.randint(1, 12)
                
                start_day = random.randint(1, 28)  # Safe day for all months
                campaign_start = date(year, start_month, start_day)
                
                # Determine status based on start date
                current_date = date(2024, 12, 31)
                days_running = (current_date - campaign_start).days
                
                if days_running > 365:  # Campaign older than 1 year
                    status = random.choice(['completed', 'completed', 'paused'])  # Likely completed
                elif days_running > 180:  # 6 months to 1 year old
                    status = random.choice(['active', 'completed', 'paused'])
                else:  # Recent campaigns
                    status = random.choice(['active', 'active', 'paused'])  # Likely active
                
                campaigns.append({
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_name,
                    'advertiser': advertiser,
                    'industry': industry,
                    'campaign_type': campaign_type,
                    'daily_budget': round(random.uniform(1000, 25000), 2),  # $1K-$25K daily budgets
                    'target_device': random.choice(devices),
                    'start_date': campaign_start,
                    'status': status
                })
                campaign_id += 1
                
                if campaign_id > num_campaigns:
                    break
            if campaign_id > num_campaigns:
                break
        if campaign_id > num_campaigns:
            break
    
    return pd.DataFrame(campaigns[:num_campaigns])

def generate_publishers(num_publishers=25):
    """Generate publishers dimension"""
    print(f"📰 Generating {num_publishers} publishers...")
    
    # Realistic publisher names by category
    publishers_data = {
        'news': ['Global News Network', 'Daily Herald', 'Breaking News Today', 'World Report', 'News Central'],
        'sports': ['Sports Zone', 'Athletic Times', 'Game Day News', 'Sports Weekly', 'Champion Report'],
        'entertainment': ['Entertainment Tonight', 'Celebrity Weekly', 'Show Business', 'Pop Culture Daily'],
        'tech': ['Tech Insider', 'Digital Trends', 'Innovation Daily', 'Future Tech', 'Code Review']
    }
    
    tiers = ['premium', 'standard']
    countries = ['US', 'UK', 'DE', 'FR', 'CA']
    
    publishers = []
    publisher_id = 1
    
    for category, pub_list in publishers_data.items():
        for pub_name in pub_list:
            if publisher_id > num_publishers:
                break
                
            tier = random.choice(tiers)
            # Premium publishers have higher traffic
            if tier == 'premium':
                monthly_visitors = random.randint(5000000, 50000000)
            else:
                monthly_visitors = random.randint(500000, 5000000)
            
            publishers.append({
                'publisher_id': publisher_id,
                'publisher_name': pub_name,
                'category': category,
                'tier': tier,
                'country': random.choice(countries),
                'monthly_visitors': monthly_visitors,
                'mobile_friendly': random.choice([True, False])
            })
            publisher_id += 1
    
    return pd.DataFrame(publishers[:num_publishers])

def generate_ad_events(num_events=2000000, campaigns_df=None, publishers_df=None):
    """Generate ad events fact table"""
    print(f"📊 Generating {num_events:,} ad events...")
    
    if campaigns_df is None or publishers_df is None:
        raise ValueError("Need campaigns and publishers dataframes")
    
    campaign_ids = campaigns_df['campaign_id'].tolist()
    publisher_ids = publishers_df['publisher_id'].tolist()
    
    event_types = ['impression', 'click', 'conversion']
    devices = ['mobile', 'desktop', 'tablet']
    countries = ['US', 'UK', 'DE', 'FR', 'CA', 'AU']
    
    events = []
    
    # Date range: 2022-01-01 to 2024-12-31 (3 years)
    start_date = date(2022, 1, 1)
    end_date = date(2024, 12, 31)
    total_days = (end_date - start_date).days + 1
    
    # Generate events in batches
    batch_size = 50000
    num_batches = (num_events + batch_size - 1) // batch_size
    
    for batch in range(num_batches):
        batch_start = batch * batch_size
        batch_end = min((batch + 1) * batch_size, num_events)
        
        print(f"  📦 Batch {batch + 1}/{num_batches} ({batch_end - batch_start:,} events)")
        
        for i in range(batch_start, batch_end):
            # Generate realistic event distribution
            event_type = np.random.choice(
                event_types, 
                p=[0.85, 0.12, 0.03]  # 85% impressions, 12% clicks, 3% conversions
            )
            
            # Realistic event costs based on industry standards
            if event_type == 'impression':
                # CPM: $0.50-$3.00 per 1000 impressions = $0.0005-$0.003 per impression
                cost = round(random.uniform(0.0005, 0.003), 4)
                revenue = None  # No revenue for impressions
            elif event_type == 'click':
                # CPC: $0.20-$5.00 per click (realistic for AdTech)
                cost = round(random.uniform(0.20, 5.00), 4)
                revenue = None  # No revenue for clicks
            else:  # conversion
                # CPA: $5.00-$50.00 per conversion (cost)
                # Revenue: $15.00-$150.00 per conversion (2-3x cost for profit)
                cost = round(random.uniform(5.00, 50.00), 4)
                revenue = round(random.uniform(15.00, 150.00), 4)
            
            # Chronological distribution across 3 years with seasonal patterns
            # More activity in Q4 (holiday season) and recent months
            year_weight = random.random()
            if year_weight < 0.2:  # 20% in 2022
                year = 2022
                month = random.randint(1, 12)
            elif year_weight < 0.4:  # 20% in 2023  
                year = 2023
                month = random.randint(1, 12)
            else:  # 60% in 2024 (more recent data)
                year = 2024
                # Seasonal weighting - more in Q4
                month_weights = [8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 15, 15]  # Higher weights for Nov/Dec
                month = random.choices(range(1, 13), weights=month_weights)[0]
            
            # Generate valid day for the month/year
            if month == 2:  # February
                max_day = 29 if year % 4 == 0 else 28
            elif month in [4, 6, 9, 11]:  # April, June, September, November
                max_day = 30
            else:
                max_day = 31
            
            day = random.randint(1, max_day)
            event_date = date(year, month, day)
            
            events.append({
                'event_id': i + 1,
                'campaign_id': random.choice(campaign_ids),
                'publisher_id': random.choice(publisher_ids),
                'event_date': event_date,
                'event_hour': random.randint(0, 23),
                'event_type': event_type,
                'device_type': random.choice(devices),
                'country': random.choice(countries),
                'cost_usd': cost,
                'revenue_usd': revenue
            })
    
    return pd.DataFrame(events)

def main():
    """Generate simplified AdTech demo data"""
    print("🚀 Generating Simplified AdTech Demo Data")
    print("🎬 Story: AutoCorp's Electric Vehicle Campaign")
    print("=" * 60)
    
    # Generate all tables
    campaigns_df = generate_campaigns(50)
    publishers_df = generate_publishers(25)
    events_df = generate_ad_events(2000000, campaigns_df, publishers_df)
    
    # Save to CSV
    print("\n💾 Saving data files...")
    
    campaigns_df.to_csv('campaigns.csv', index=False)
    print(f"✅ campaigns.csv ({len(campaigns_df):,} records)")
    
    publishers_df.to_csv('publishers.csv', index=False)
    print(f"✅ publishers.csv ({len(publishers_df):,} records)")
    
    events_df.to_csv('ad_events.csv', index=False)
    print(f"✅ ad_events.csv ({len(events_df):,} records)")
    
    # Show sample data for verification
    print(f"\n📋 Sample Data Preview:")
    print("\n🏢 Top Campaigns by Budget:")
    print(campaigns_df.nlargest(5, 'daily_budget')[['campaign_name', 'advertiser', 'daily_budget', 'status']])
    
    print(f"\n📰 Publishers by Tier:")
    print(publishers_df.groupby('tier').size().to_string())
    
    print(f"\n📊 Events by Type:")
    print(events_df['event_type'].value_counts().to_string())
    
    # MANDATORY CONSISTENCY CHECKS
    print(f"\n🔍 Running Mandatory Consistency Checks...")
    
    # Check 1: Foreign Key Integrity
    campaign_ids_in_campaigns = set(campaigns_df['campaign_id'])
    campaign_ids_in_events = set(events_df['campaign_id'])
    publisher_ids_in_publishers = set(publishers_df['publisher_id'])
    publisher_ids_in_events = set(events_df['publisher_id'])
    
    orphaned_campaigns = campaign_ids_in_events - campaign_ids_in_campaigns
    orphaned_publishers = publisher_ids_in_events - publisher_ids_in_publishers
    
    if orphaned_campaigns:
        raise ValueError(f"❌ CONSISTENCY ERROR: Orphaned campaign IDs in events: {orphaned_campaigns}")
    if orphaned_publishers:
        raise ValueError(f"❌ CONSISTENCY ERROR: Orphaned publisher IDs in events: {orphaned_publishers}")
    
    print(f"✅ Foreign Key Integrity: All event references are valid")
    
    # Check 2: Date Range Validation
    min_event_date = events_df['event_date'].min()
    max_event_date = events_df['event_date'].max()
    min_campaign_date = campaigns_df['start_date'].min()
    max_campaign_date = campaigns_df['start_date'].max()
    
    print(f"✅ Date Ranges:")
    print(f"   📅 Events: {min_event_date} to {max_event_date}")
    print(f"   📅 Campaigns: {min_campaign_date} to {max_campaign_date}")
    
    # Check 3: Revenue Logic Validation  
    impression_with_revenue = events_df[(events_df['event_type'] == 'impression') & (events_df['revenue_usd'].notna())]
    click_with_revenue = events_df[(events_df['event_type'] == 'click') & (events_df['revenue_usd'].notna())]
    conversion_without_revenue = events_df[(events_df['event_type'] == 'conversion') & (events_df['revenue_usd'].isna())]
    
    if len(impression_with_revenue) > 0:
        raise ValueError(f"❌ CONSISTENCY ERROR: {len(impression_with_revenue)} impressions have revenue")
    if len(click_with_revenue) > 0:
        raise ValueError(f"❌ CONSISTENCY ERROR: {len(click_with_revenue)} clicks have revenue")
    if len(conversion_without_revenue) > 0:
        raise ValueError(f"❌ CONSISTENCY ERROR: {len(conversion_without_revenue)} conversions missing revenue")
    
    print(f"✅ Revenue Logic: Only conversions have revenue")
    
    # Check 4: Record Count Validation
    expected_events = 2000000
    actual_events = len(events_df)
    if actual_events != expected_events:
        raise ValueError(f"❌ CONSISTENCY ERROR: Expected {expected_events} events, got {actual_events}")
    
    print(f"✅ Record Counts: {actual_events:,} events generated")
    
    # Check 5: Join Preview (sample join to verify data works together)
    sample_join = events_df.merge(campaigns_df, on='campaign_id').merge(publishers_df, on='publisher_id')
    if len(sample_join) == 0:
        raise ValueError(f"❌ CONSISTENCY ERROR: Sample joins produce no results")
    
    print(f"✅ Join Validation: Sample 3-table join produces {len(sample_join):,} results")
    
    print(f"\n🎉 ALL CONSISTENCY CHECKS PASSED! Demo data ready!")
    print(f"💡 Upload to S3 and run setup_simple_adtech.sql in Firebolt")

if __name__ == "__main__":
    main()
