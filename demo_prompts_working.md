# 🎯 Demo Prompts - Working Set for Live Demo

## 📋 **5 Core Demo Prompts** 

These prompts are designed to showcase Claude's NL2SQL capabilities and Firebolt's performance with the AdTech schema.

---

### **1. Campaign Performance Overview**
**"Show me the total conversions and revenue for each campaign type for AutoCorp"**

*Perfect for*: Basic aggregation and joins
*Expected Result*: 3 rows showing search, display, video performance
*Visualization*: Bar chart comparing campaign types

```sql
SELECT 
    c.campaign_type,
    COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) as total_conversions,
    SUM(ae.revenue_usd) as total_revenue
FROM campaigns c
JOIN ad_events ae ON c.campaign_id = ae.campaign_id
WHERE c.advertiser = 'AutoCorp'
GROUP BY c.campaign_type
ORDER BY total_revenue DESC;
```

---

### **2. Publisher Performance Analysis**
**"Which publishers are performing best for AutoCorp in terms of conversion rate and revenue?"**

*Perfect for*: Complex joins across all 3 tables
*Expected Result*: Publisher ranking with conversion metrics
*Visualization*: Multi-metric comparison

```sql
SELECT 
    p.publisher_name,
    p.region,
    COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) as conversions,
    COUNT(ae.event_id) as total_events,
    ROUND(COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) * 100.0 / NULLIF(COUNT(ae.event_id), 0), 2) as conversion_rate,
    SUM(ae.revenue_usd) as total_revenue
FROM campaigns c
JOIN ad_events ae ON c.campaign_id = ae.campaign_id
JOIN publishers p ON ae.publisher_id = p.publisher_id
WHERE c.advertiser = 'AutoCorp'
GROUP BY p.publisher_name, p.region
HAVING COUNT(ae.event_id) > 100
ORDER BY conversion_rate DESC, total_revenue DESC
LIMIT 10;
```

---

### **3. Hourly Performance Trends (CTE Example)**
**"Show me AutoCorp's hourly conversion patterns with revenue trends"**

*Perfect for*: CTEs, window functions, time analysis
*Expected Result*: Hourly breakdown with trends
*Visualization*: Time-series line chart

```sql
WITH hourly_stats AS (
    SELECT 
        ae.event_hour,
        COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) as conversions,
        SUM(ae.revenue_usd) as revenue,
        COUNT(ae.event_id) as total_events
    FROM campaigns c
    JOIN ad_events ae ON c.campaign_id = ae.campaign_id
    WHERE c.advertiser = 'AutoCorp'
    GROUP BY ae.event_hour
)
SELECT 
    event_hour,
    conversions,
    revenue,
    ROUND(conversions * 100.0 / NULLIF(total_events, 0), 2) as conversion_rate,
    LAG(revenue) OVER (ORDER BY event_hour) as prev_hour_revenue
FROM hourly_stats
ORDER BY event_hour;
```

---

### **4. Cost Efficiency Analysis**
**"What's the cost per conversion and ROI for each of AutoCorp's campaign types?"**

*Perfect for*: Advanced calculations, business metrics
*Expected Result*: ROI and efficiency metrics by campaign type
*Visualization*: Efficiency comparison chart

```sql
SELECT 
    c.campaign_type,
    COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) as total_conversions,
    SUM(ae.cost_usd) as total_cost,
    SUM(ae.revenue_usd) as total_revenue,
    ROUND(SUM(ae.cost_usd) / NULLIF(COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END), 0), 2) as cost_per_conversion,
    ROUND((SUM(ae.revenue_usd) - SUM(ae.cost_usd)) / NULLIF(SUM(ae.cost_usd), 0) * 100, 2) as roi_percentage
FROM campaigns c
JOIN ad_events ae ON c.campaign_id = ae.campaign_id
WHERE c.advertiser = 'AutoCorp'
GROUP BY c.campaign_type
HAVING COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) > 0
ORDER BY roi_percentage DESC;
```

---

### **5. Regional Campaign Performance**
**"Break down AutoCorp's campaign performance by publisher region and campaign type"**

*Perfect for*: Multi-dimensional analysis, complex grouping
*Expected Result*: Matrix of region x campaign type performance
*Visualization*: Heatmap-style comparison

```sql
SELECT 
    p.region,
    c.campaign_type,
    COUNT(DISTINCT c.campaign_id) as active_campaigns,
    COUNT(CASE WHEN ae.event_type = 'conversion' THEN 1 END) as conversions,
    SUM(ae.revenue_usd) as revenue,
    AVG(ae.revenue_usd) as avg_revenue_per_event
FROM campaigns c
JOIN ad_events ae ON c.campaign_id = ae.campaign_id
JOIN publishers p ON ae.publisher_id = p.publisher_id
WHERE c.advertiser = 'AutoCorp'
GROUP BY p.region, c.campaign_type
ORDER BY p.region, revenue DESC;
```

---

## 🎯 **Enhanced SQL Validation**

### **Supported Query Types:**
- ✅ `SELECT` statements
- ✅ `WITH` (Common Table Expressions)
- ✅ `EXPLAIN` (query plans)
- ✅ `DESCRIBE` (table structure)
- ✅ `SHOW` (metadata queries)
- ✅ `VALUES` (value lists)
- ✅ `(SELECT` (subqueries)
- ✅ `(WITH` (parenthesized CTEs)

### **Blocked Query Types:**
- ❌ `INSERT`, `UPDATE`, `DELETE` (DML)
- ❌ `CREATE`, `ALTER`, `DROP` (DDL)
- ❌ `GRANT`, `REVOKE` (DCL)
- ❌ `CALL`, `EXEC` (Procedural)

---

## 📊 **Visualization-Perfect Prompts**

### **6. Revenue Trend Over Time (LINE CHART PERFECT)**
**"Show me AutoCorp's hourly revenue trend for their campaigns"**

*Perfect for*: Automatic line chart generation
*Expected Result*: Time-series data showing revenue patterns by hour
*Visualization*: Beautiful line chart showing revenue trends

```sql
SELECT 
    e.event_hour,
    SUM(e.revenue_usd) as hourly_revenue,
    COUNT(CASE WHEN e.event_type = 'conversion' THEN 1 END) as hourly_conversions
FROM ad_events e
JOIN campaigns c ON e.campaign_id = c.campaign_id
WHERE c.advertiser = 'AutoCorp'
GROUP BY e.event_hour
ORDER BY e.event_hour
LIMIT 24;
```

---

### **7. Campaign Budget Distribution (PIE CHART PERFECT)**
**"What's the budget distribution across AutoCorp's different campaign types?"**

*Perfect for*: Categorical data visualization with pie chart option
*Expected Result*: Campaign type breakdown with budget allocation (3 categories)
*Visualization*: Smart suggestion will recommend "🥧 Pie Chart (Distribution)" - perfect for showing proportions

```sql
SELECT 
    c.campaign_type,
    SUM(c.daily_budget) as total_budget,
    COUNT(DISTINCT c.campaign_id) as campaign_count
FROM campaigns c
WHERE c.advertiser = 'AutoCorp'
GROUP BY c.campaign_type
ORDER BY total_budget DESC;
```

---

## 🎭 **Demo Flow Strategy**

### **Opening (Prompts 1-2):**
- Start with simple aggregations to show basic NL2SQL
- Demonstrate multi-table joins
- Highlight sub-second query performance

### **Advanced (Prompts 3-5):**
- Showcase complex SQL generation (CTEs, window functions)
- Business intelligence calculations
- Multi-dimensional analysis

### **Visualization (Prompts 6-7):**
- Perfect data for automatic chart suggestions
- Interactive visualization creation
- Professional chart presentation

### **Performance Showcase:**
- Use "Get Firebolt Engine Time" after each query
- Highlight sub-second execution times
- Compare total response time vs engine time

---

## 🚀 **Demo Success Metrics**

### **NL2SQL Accuracy:**
- ✅ All 7 prompts generate valid Firebolt SQL
- ✅ CTEs and complex functions work correctly
- ✅ Business logic accurately translated

### **Performance Demonstration:**
- ⚡ Sub-second query execution on 2M+ records
- 📊 Real-time visualization generation
- 🔥 Firebolt engine time tracking

### **Visual Impact:**
- 📈 Interactive charts for every query result
- 🎨 Professional UI with Firebolt branding
- ✨ Smooth user experience throughout

**These prompts are battle-tested and guaranteed to work perfectly with the current schema and application! 🎯✨**
