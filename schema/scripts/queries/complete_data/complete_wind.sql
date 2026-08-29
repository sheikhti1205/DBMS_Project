-- Wind rows with both minimum and maximum readings available.
SELECT Station_Name,
       Year,
       Month,
       Maximum_Wind_Speed,
       Maximum_Wind_Direction,
       Minimum_Wind_Speed,
       Minimum_Wind_Direction
FROM Monthly_Wind_Summary
WHERE Station_Name IS NOT NULL
  AND TRIM(Station_Name) <> ''
  AND Year IS NOT NULL
  AND Month IS NOT NULL
  AND Maximum_Wind_Speed IS NOT NULL
  AND Maximum_Wind_Direction IS NOT NULL
  AND Minimum_Wind_Speed IS NOT NULL
  AND Minimum_Wind_Direction IS NOT NULL
ORDER BY Year DESC, Month DESC, Station_Name;
