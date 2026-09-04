-- name: climate
-- Monthly climate measurements with minimum and maximum side by side.
SELECT Station_Name,
       Year,
       Month,
       Maximum_Temperature,
       Minimum_Temperature,
       Humidity,
       Rainfall,
       Thunderstorm,
       Lightning
FROM Monthly_Climate_Summary
ORDER BY Year DESC, Month DESC, Station_Name
LIMIT 50;

-- name: wind
-- Monthly wind readings with minimum and maximum side by side.
SELECT Station_Name,
       Year,
       Month,
       Maximum_Wind_Speed,
       Maximum_Wind_Direction,
       Minimum_Wind_Speed,
       Minimum_Wind_Direction
FROM Monthly_Wind_Summary
ORDER BY Year DESC, Month DESC, Station_Name
LIMIT 50;

-- name: rivers
-- Water-quality readings with their river names.
SELECT rs.River_Name,
       w.WQ_Station_Name,
       w.Year,
       w.Parameter_Type,
       w.Value
FROM Water_Quality AS w
JOIN River_Station AS rs
  ON rs.WQ_Station_Name = w.WQ_Station_Name
ORDER BY w.Year DESC, rs.River_Name, w.WQ_Station_Name, w.Parameter_Type
LIMIT 50;

-- name: wastewater
-- Produced waste-water volume and source-derived reuse percentage.
SELECT Industry_Name,
       Start_Year,
       End_Year,
       Quantity,
       ROUND(Percentage, 2) AS Percentage
FROM Industry_Usage
ORDER BY Start_Year DESC, Industry_Name
LIMIT 50;

-- name: forests
-- Forest land by district and fiscal year.
SELECT District_Name,
       Fiscal_Start_Year,
       Fiscal_End_Year,
       Protected_Area,
       Total_Forest_FD_Acre,
       Total_Forest_Land
FROM Forest_Area_Record
ORDER BY Fiscal_Start_Year DESC, District_Name
LIMIT 50;

-- name: table-counts
-- Record counts for every table, followed by the database total.
WITH counts(Table_Name, Records, Sort_Order) AS (
  SELECT 'Year_Time', COUNT(*), 1 FROM Year_Time UNION ALL
  SELECT 'Month_Time', COUNT(*), 2 FROM Month_Time UNION ALL
  SELECT 'Day_Time', COUNT(*), 3 FROM Day_Time UNION ALL
  SELECT 'Fiscal_Year', COUNT(*), 4 FROM Fiscal_Year UNION ALL
  SELECT 'Station', COUNT(*), 5 FROM Station UNION ALL
  SELECT 'District', COUNT(*), 6 FROM District UNION ALL
  SELECT 'River', COUNT(*), 7 FROM River UNION ALL
  SELECT 'River_Station', COUNT(*), 8 FROM River_Station UNION ALL
  SELECT 'Size', COUNT(*), 9 FROM Size UNION ALL
  SELECT 'Industry_Type', COUNT(*), 10 FROM Industry_Type UNION ALL
  SELECT 'Temperature_Record', COUNT(*), 11 FROM Temperature_Record UNION ALL
  SELECT 'Humidity_Record', COUNT(*), 12 FROM Humidity_Record UNION ALL
  SELECT 'Rainfall_Record', COUNT(*), 13 FROM Rainfall_Record UNION ALL
  SELECT 'Wind_Record', COUNT(*), 14 FROM Wind_Record UNION ALL
  SELECT 'Climatic_Event_Record', COUNT(*), 15 FROM Climatic_Event_Record UNION ALL
  SELECT 'Sunshine_Record', COUNT(*), 16 FROM Sunshine_Record UNION ALL
  SELECT 'Radiation_Record', COUNT(*), 17 FROM Radiation_Record UNION ALL
  SELECT 'Water_Quality', COUNT(*), 18 FROM Water_Quality UNION ALL
  SELECT 'Forest_Area_Record', COUNT(*), 19 FROM Forest_Area_Record UNION ALL
  SELECT 'Type_Of_Establishments', COUNT(*), 20 FROM Type_Of_Establishments UNION ALL
  SELECT 'Industry_Usage', COUNT(*), 21 FROM Industry_Usage
), final_counts(Table_Name, Records, Sort_Group) AS (
  SELECT Table_Name, Records, 1 FROM counts
  UNION ALL
  SELECT 'TOTAL', SUM(Records), 2 FROM counts
)
SELECT Table_Name, Records
FROM final_counts
ORDER BY Sort_Group, Table_Name;

-- name: relationships
-- Foreign-key relationships currently enforced by SQLite.
SELECT m.name AS Child_Table,
       GROUP_CONCAT(f."from", ', ') AS Child_Columns,
       f."table" AS Parent_Table,
       GROUP_CONCAT(f."to", ', ') AS Parent_Columns
FROM sqlite_schema AS m
JOIN pragma_foreign_key_list(m.name) AS f
WHERE m.type = 'table'
  AND m.name NOT LIKE 'sqlite_%'
GROUP BY m.name, f.id, f."table"
ORDER BY m.name, f.id;

-- name: time-coverage
-- Available year ranges for the time-based record tables.
SELECT 'Temperature_Record' AS Relation, MIN(Year) AS First_Year, MAX(Year) AS Last_Year FROM Temperature_Record
UNION ALL SELECT 'Humidity_Record', MIN(Year), MAX(Year) FROM Humidity_Record
UNION ALL SELECT 'Rainfall_Record', MIN(Year), MAX(Year) FROM Rainfall_Record
UNION ALL SELECT 'Wind_Record', MIN(Year), MAX(Year) FROM Wind_Record
UNION ALL SELECT 'Climatic_Event_Record', MIN(Year), MAX(Year) FROM Climatic_Event_Record
UNION ALL SELECT 'Sunshine_Record', MIN(Year), MAX(Year) FROM Sunshine_Record
UNION ALL SELECT 'Radiation_Record', MIN(Year), MAX(Year) FROM Radiation_Record
UNION ALL SELECT 'Water_Quality', MIN(Year), MAX(Year) FROM Water_Quality
UNION ALL SELECT 'Forest_Area_Record', MIN(Fiscal_Start_Year), MAX(Fiscal_End_Year) FROM Forest_Area_Record
UNION ALL SELECT 'Type_Of_Establishments', MIN(Start_Year), MAX(End_Year) FROM Type_Of_Establishments
UNION ALL SELECT 'Industry_Usage', MIN(Start_Year), MAX(End_Year) FROM Industry_Usage
ORDER BY Relation;

-- name: rainfall-ranking
-- Stations ranked by average reported monthly rainfall.
SELECT Station_Name,
       COUNT(*) AS Measurements,
       ROUND(AVG(Rainfall), 2) AS Average_Rainfall,
       ROUND(MAX(Rainfall), 2) AS Highest_Rainfall
FROM Rainfall_Record
WHERE Rainfall IS NOT NULL
GROUP BY Station_Name
HAVING COUNT(*) >= 100
ORDER BY Average_Rainfall DESC, Station_Name
LIMIT 15;

-- name: water-quality-summary
-- Water-quality coverage summarized by river and parameter.
SELECT rs.River_Name,
       w.Parameter_Type,
       COUNT(*) AS Measurements,
       MIN(w.Year) AS First_Year,
       MAX(w.Year) AS Last_Year,
       ROUND(AVG(w.Value), 3) AS Average_Value
FROM Water_Quality AS w
JOIN River_Station AS rs
  ON rs.WQ_Station_Name = w.WQ_Station_Name
WHERE w.Value IS NOT NULL
GROUP BY rs.River_Name, w.Parameter_Type
ORDER BY Measurements DESC, rs.River_Name, w.Parameter_Type
LIMIT 25;

-- name: missing-measurements
-- Null measurement counts without treating missing values as zero.
SELECT 'Temperature_Record.Temp' AS Field,
       SUM(CASE WHEN Temp IS NULL THEN 1 ELSE 0 END) AS Missing,
       COUNT(*) AS Total
FROM Temperature_Record
UNION ALL
SELECT 'Humidity_Record.Humidity', SUM(CASE WHEN Humidity IS NULL THEN 1 ELSE 0 END), COUNT(*) FROM Humidity_Record
UNION ALL
SELECT 'Rainfall_Record.Rainfall', SUM(CASE WHEN Rainfall IS NULL THEN 1 ELSE 0 END), COUNT(*) FROM Rainfall_Record
UNION ALL
SELECT 'Wind_Record.Wind_Speed', SUM(CASE WHEN Wind_Speed IS NULL THEN 1 ELSE 0 END), COUNT(*) FROM Wind_Record
UNION ALL
SELECT 'Wind_Record.Direction', SUM(CASE WHEN Direction IS NULL THEN 1 ELSE 0 END), COUNT(*) FROM Wind_Record
UNION ALL
SELECT 'Water_Quality.Value', SUM(CASE WHEN Value IS NULL THEN 1 ELSE 0 END), COUNT(*) FROM Water_Quality
ORDER BY Field;

-- name: integrity
-- SQLite's complete database integrity result.
PRAGMA integrity_check;

-- name: foreign-key-check
-- Returns no rows when every foreign key is valid.
PRAGMA foreign_key_check;
