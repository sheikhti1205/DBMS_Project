-- name: climate
-- Monthly climate measurements by station.
SELECT t.Station_Name,
       t.Year,
       t.Month,
       t.Type AS Temperature_Type,
       t.Temp,
       h.Humidity,
       r.Rainfall
FROM Temperature_Record AS t
LEFT JOIN Humidity_Record AS h
  ON h.Station_Name = t.Station_Name
 AND h.Year = t.Year
 AND h.Month = t.Month
LEFT JOIN Rainfall_Record AS r
  ON r.Station_Name = t.Station_Name
 AND r.Year = t.Year
 AND r.Month = t.Month
ORDER BY t.Year DESC, t.Month DESC, t.Station_Name, t.Type
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
-- Waste-water production, reuse, and calculated reuse rate.
SELECT Industry_Name,
       Start_Year,
       End_Year,
       Produced_Waste_Water,
       Reused_Waste_Water,
       ROUND(Reuse_Percentage, 2) AS Reuse_Percentage
FROM Industry_Usage_With_Rate
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
