-- Forest records where every displayed area measurement is available.
SELECT District_Name,
       Fiscal_Start_Year,
       Fiscal_End_Year,
       Protected_Area,
       Total_Forest_FD_Acre,
       Total_Forest_Land
FROM Forest_Area_Record
WHERE District_Name IS NOT NULL
  AND TRIM(District_Name) <> ''
  AND Fiscal_Start_Year IS NOT NULL
  AND Fiscal_End_Year IS NOT NULL
  AND Protected_Area IS NOT NULL
  AND Total_Forest_FD_Acre IS NOT NULL
  AND Total_Forest_Land IS NOT NULL
ORDER BY Fiscal_Start_Year DESC, District_Name;
