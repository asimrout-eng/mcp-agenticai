-- =======================================================
-- SIMPLIFIED ADTECH DEMO SETUP
-- Story: AutoCorp's Electric Vehicle Marketing Campaign
-- =======================================================

-- Step 1: Create S3 location (UPDATE WITH YOUR CREDENTIALS)
CREATE LOCATION simple_adtech_location WITH 
SOURCE = AMAZON_S3 
CREDENTIALS = ( 
    AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY' 
    AWS_SECRET_ACCESS_KEY='YOUR_SECRET_KEY' 
) 
URL = 's3://your-bucket/simple-adtech/';

-- =======================================================
-- DROP EXISTING TABLES
-- =======================================================
DROP TABLE IF EXISTS ad_events;
DROP TABLE IF EXISTS publishers;
DROP TABLE IF EXISTS campaigns;

-- =======================================================
-- CREATE TABLES
-- =======================================================

-- Campaigns dimension
CREATE DIMENSION TABLE campaigns (
    campaign_id         INTEGER,
    campaign_name       TEXT,
    advertiser          TEXT,
    industry            TEXT,
    campaign_type       TEXT,
    daily_budget        DECIMAL(10,2),
    target_device       TEXT,
    start_date          DATE,
    status              TEXT
)
PRIMARY INDEX campaign_id;

-- Publishers dimension
CREATE DIMENSION TABLE publishers (
    publisher_id        INTEGER,
    publisher_name      TEXT,
    category            TEXT,
    tier                TEXT,
    country             TEXT,
    monthly_visitors    BIGINT,
    mobile_friendly     BOOLEAN
)
PRIMARY INDEX publisher_id;

-- Ad events fact table
CREATE FACT TABLE ad_events (
    event_id           BIGINT,
    campaign_id        INTEGER,
    publisher_id       INTEGER,
    event_date         DATE,
    event_hour         INTEGER,
    event_type         TEXT,
    device_type        TEXT,
    country            TEXT,
    cost_usd           DECIMAL(15,4),
    revenue_usd        DECIMAL(15,4)
)
PRIMARY INDEX campaign_id, event_date
PARTITION BY event_date;

-- =======================================================
-- LOAD DATA
-- =======================================================

-- Load campaigns
COPY INTO campaigns
FROM simple_adtech_location
PATTERN = 'campaigns.csv'
TYPE = CSV
HEADER = TRUE;

-- Load publishers
COPY INTO publishers
FROM simple_adtech_location
PATTERN = 'publishers.csv'
TYPE = CSV
HEADER = TRUE;

-- Load ad events
COPY INTO ad_events
FROM simple_adtech_location
PATTERN = 'ad_events.csv'
TYPE = CSV
HEADER = TRUE;



