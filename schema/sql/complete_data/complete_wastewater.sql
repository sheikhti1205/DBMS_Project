-- Wastewater records with complete industry, period, volume, and percentage data.
SELECT Industry_Name,
       Start_Year,
       End_Year,
       Quantity,
       ROUND(Percentage, 2) AS Percentage
FROM Industry_Usage
WHERE Industry_Name IS NOT NULL
  AND TRIM(Industry_Name) <> ''
  AND Start_Year IS NOT NULL
  AND End_Year IS NOT NULL
  AND Quantity IS NOT NULL
  AND Percentage IS NOT NULL
ORDER BY Start_Year DESC, Industry_Name;
