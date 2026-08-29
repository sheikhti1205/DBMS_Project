-- Climate rows where every displayed measurement is available.
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
WHERE Station_Name IS NOT NULL
  AND TRIM(Station_Name) <> ''
  AND Year IS NOT NULL
  AND Month IS NOT NULL
  AND Maximum_Temperature IS NOT NULL
  AND Minimum_Temperature IS NOT NULL
  AND Humidity IS NOT NULL
  AND Rainfall IS NOT NULL
  AND Thunderstorm IS NOT NULL
  AND Lightning IS NOT NULL
ORDER BY Year DESC, Month DESC, Station_Name;
