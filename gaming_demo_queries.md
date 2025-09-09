# Gaming Demo Queries - Final Version

## 🎮 Final 4 Demo Queries for Gaming Analytics

### 🟢 **Query 1: Simple - Player Base Overview**

**Business Context:** Geographic Distribution - Player base analysis
**Complexity:** Simple (1 table)
**Tables Used:** `players`

**Natural Language Prompt:**
> **"Show me the count of players by country"**

**Expected SQL:**
```sql
SELECT country, COUNT(*) as player_count 
FROM players 
GROUP BY country 
ORDER BY player_count DESC
```

**Business Value:**
- Player base geographic distribution
- Market size analysis by region
- Localization planning insights
- Marketing budget allocation guidance

**Visualization:** Bar chart showing player count by country

---

### 🟡 **Query 2: Intermediate - Player Event Analysis**

**Business Context:** Game Engagement - Performance analysis with 2-table join
**Complexity:** Intermediate (2 tables with JOIN)
**Tables Used:** `player_events_big` + `games`

**Natural Language Prompt:**
> **"Show me total events and average event level by game type from player event data"**

**Expected SQL:**
```sql
SELECT g.game_type,
       COUNT(pe.event_id) as total_events,
       AVG(pe.level) as avg_event_level
FROM games g
JOIN player_events_big pe ON g.game_id = pe.game_id
GROUP BY g.game_type
ORDER BY total_events DESC
```

**Business Value:**
- Game engagement comparison
- Product development prioritization
- Player behavior insights by game type
- Feature usage analysis

**Visualization:** Bar chart comparing event activity across game types

---

### 🟠 **Query 3: External Table - Regional Event Analysis**

**Business Context:** External Data Integration - Real-time event stream analysis
**Complexity:** Intermediate (External table + Internal table JOIN)
**Tables Used:** `ext_iceberg_player_events` (external) + `players` (internal)

**Natural Language Prompt:**
> **"Show me player event activity by country using our external event data, including total events and unique players"**

**Expected SQL:**
```sql
SELECT p.country, 
       COUNT(*) as total_events, 
       COUNT(DISTINCT e.player_id) as unique_players 
FROM ext_iceberg_player_events e 
JOIN players p ON e.player_id = p.player_id 
GROUP BY p.country 
ORDER BY total_events DESC
```

**Business Value:**
- Real-time regional engagement analysis
- External data integration showcase
- Geographic event pattern insights
- Marketing strategy optimization

**Visualization:** Bar chart showing event activity by country

---

### 🔴 **Query 4: Advanced - Premium Player Performance**

**Business Context:** Advanced Analytics - Multi-table premium player insights
**Complexity:** Advanced (3 tables with multiple JOINs)
**Tables Used:** `players` + `games` + `player_events_big`

**Natural Language Prompt:**
> **"Show me premium players with their average game score and total events, grouped by country"**

**Expected SQL:**
```sql
SELECT p.country,
       COUNT(DISTINCT p.player_id) as premium_players,
       AVG(g.score) as avg_game_score,
       COUNT(DISTINCT pe.event_id) as total_events
FROM players p
JOIN games g ON p.player_id = g.player_id
JOIN player_events_big pe ON p.player_id = pe.player_id
WHERE p.is_premium = true
GROUP BY p.country
HAVING COUNT(DISTINCT p.player_id) >= 5
ORDER BY avg_game_score DESC
```

**Business Value:**
- Premium player performance analysis
- Geographic premium user insights
- Revenue optimization opportunities
- High-value customer segmentation

**Visualization:** Scatter plot or table showing premium player metrics by country

---

## 🎯 Demo Progression Strategy

### **📈 Complexity Escalation:**
1. **Start Simple**: Geographic distribution (always works)
2. **Show Joins**: Event analysis with 2-table join
3. **External Integration**: Real-time external data showcase
4. **Advanced Analytics**: Complex multi-table premium insights

### **🚀 Business Narrative:**
1. **Foundation**: "Where are our players?" (Geographic analysis)
2. **Engagement**: "How do players interact with different games?" (Behavioral analysis)
3. **Real-time**: "What's happening right now?" (External data integration)
4. **Strategic**: "Who are our most valuable players?" (Premium analysis)

### **📊 Visualization Ready:**
- **Query 1**: Bar chart (Geographic distribution)
- **Query 2**: Bar chart (Game type comparison)
- **Query 3**: Bar chart (Regional event activity)
- **Query 4**: Table/Scatter plot (Premium player metrics)

---

## 🔧 Technical Details

### **Table Coverage:**
- **Base Tables**: `players`, `games`, `player_events_big`
- **External Tables**: `ext_iceberg_player_events`
- **Join Patterns**: Single table → 2-table → External+Internal → 3-table

### **SQL Features Demonstrated:**
- **Basic Aggregation**: COUNT, GROUP BY, ORDER BY
- **JOINs**: INNER JOIN across multiple tables
- **External Tables**: Integration with external data sources
- **Filtering**: WHERE clauses and HAVING clauses
- **Advanced Aggregation**: Multiple aggregations with DISTINCT

### **Demo Benefits:**
- ✅ **Progressive complexity**: Each query builds on the previous
- ✅ **Business relevance**: Real gaming industry scenarios
- ✅ **Technical showcase**: Covers all major SQL patterns
- ✅ **Reliable execution**: Tested and verified queries
- ✅ **Visualization ready**: All queries produce chart-friendly results

This progression perfectly demonstrates the power of NL2SQL with Firebolt across different complexity levels and use cases! 🎮


