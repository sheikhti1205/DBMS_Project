-- Water-quality readings with complete river, station, parameter, and value data.
SELECT rs.River_Name,
       w.WQ_Station_Name,
       w.Year,
       w.Parameter_Type,
       w.Value
FROM Water_Quality AS w
JOIN River_Station AS rs
  ON rs.WQ_Station_Name = w.WQ_Station_Name
WHERE rs.River_Name IS NOT NULL
  AND TRIM(rs.River_Name) <> ''
  AND w.WQ_Station_Name IS NOT NULL
  AND TRIM(w.WQ_Station_Name) <> ''
  AND w.Year IS NOT NULL
  AND w.Parameter_Type IS NOT NULL
  AND TRIM(w.Parameter_Type) <> ''
  AND w.Value IS NOT NULL
ORDER BY w.Year DESC,
         rs.River_Name,
         w.WQ_Station_Name,
         w.Parameter_Type;
