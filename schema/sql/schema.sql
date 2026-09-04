PRAGMA foreign_keys = ON;

CREATE TABLE "Year_Time" (
  "Year" INTEGER NOT NULL,
  PRIMARY KEY ("Year"),
  CHECK ("Year" BETWEEN 1900 AND 2100)
);

CREATE TABLE "Month_Time" (
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  PRIMARY KEY ("Year", "Month"),
  FOREIGN KEY ("Year") REFERENCES "Year_Time" ("Year"),
  CHECK ("Month" BETWEEN 1 AND 12)
);

CREATE TABLE "Day_Time" (
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Day" INTEGER NOT NULL,
  PRIMARY KEY ("Year", "Month", "Day"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month"),
  CHECK ("Month" BETWEEN 1 AND 12),
  CHECK ("Day" BETWEEN 1 AND 31),
  CHECK (strftime('%Y-%m-%d', printf('%04d-%02d-%02d', "Year", "Month", "Day")) = printf('%04d-%02d-%02d', "Year", "Month", "Day"))
);

CREATE TABLE "Fiscal_Year" (
  "Start_Year" INTEGER NOT NULL,
  "End_Year" INTEGER NOT NULL,
  PRIMARY KEY ("Start_Year", "End_Year"),
  FOREIGN KEY ("Start_Year") REFERENCES "Year_Time" ("Year"),
  FOREIGN KEY ("End_Year") REFERENCES "Year_Time" ("Year"),
  CHECK ("End_Year" = "Start_Year" + 1)
);

CREATE TABLE "District" (
  "District_Name" TEXT NOT NULL,
  PRIMARY KEY ("District_Name")
);

CREATE TABLE "Station" (
  "Station_Name" TEXT NOT NULL,
  "District_Name" TEXT,
  PRIMARY KEY ("Station_Name"),
  FOREIGN KEY ("District_Name") REFERENCES "District" ("District_Name")
);

CREATE TABLE "River" (
  "River_Name" TEXT NOT NULL,
  PRIMARY KEY ("River_Name")
);

CREATE TABLE "River_Station" (
  "WQ_Station_Name" TEXT NOT NULL,
  "River_Name" TEXT NOT NULL,
  PRIMARY KEY ("WQ_Station_Name"),
  FOREIGN KEY ("River_Name") REFERENCES "River" ("River_Name")
);

CREATE TABLE "Size" (
  "Size_Name" TEXT NOT NULL,
  PRIMARY KEY ("Size_Name")
);

CREATE TABLE "Industry_Type" (
  "Industry_Name" TEXT NOT NULL,
  PRIMARY KEY ("Industry_Name")
);

CREATE TABLE "Temperature_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Type" TEXT NOT NULL,
  "Temp" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month", "Type"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month"),
  CHECK ("Type" IN ('Maximum', 'Minimum')),
  CHECK ("Temp" IS NULL OR "Temp" BETWEEN -5 AND 50)
);

CREATE TABLE "Humidity_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Humidity" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month"),
  CHECK ("Humidity" IS NULL OR "Humidity" BETWEEN 0 AND 100)
);

CREATE TABLE "Rainfall_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Rainfall" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month"),
  CHECK ("Rainfall" IS NULL OR "Rainfall" BETWEEN 0 AND 3000)
);

CREATE TABLE "Wind_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Type" TEXT NOT NULL,
  "Wind_Speed" REAL,
  "Direction" TEXT,
  PRIMARY KEY ("Station_Name", "Year", "Month", "Type"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month"),
  CHECK ("Type" IN ('Maximum', 'Minimum')),
  CHECK ("Wind_Speed" IS NULL OR "Wind_Speed" BETWEEN 0 AND 250)
);

CREATE TABLE "Climatic_Event_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Thunderstorm" REAL,
  "Lightning" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month"),
  CHECK ("Thunderstorm" IS NULL OR "Thunderstorm" >= 0),
  CHECK ("Lightning" IS NULL OR "Lightning" >= 0)
);

CREATE TABLE "Sunshine_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Day" INTEGER NOT NULL,
  "Sunshine_Hours" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month", "Day"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month", "Day") REFERENCES "Day_Time" ("Year", "Month", "Day"),
  CHECK ("Sunshine_Hours" IS NULL OR "Sunshine_Hours" BETWEEN 0 AND 14)
);

CREATE TABLE "Radiation_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Day" INTEGER NOT NULL,
  "Sample_No" INTEGER NOT NULL,
  "Radiation" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month", "Day", "Sample_No"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month", "Day") REFERENCES "Day_Time" ("Year", "Month", "Day"),
  CHECK ("Sample_No" >= 0),
  CHECK ("Radiation" IS NULL OR "Radiation" >= 0)
);

CREATE TABLE "Water_Quality" (
  "WQ_Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Parameter_Type" TEXT NOT NULL,
  "Value" REAL,
  PRIMARY KEY ("WQ_Station_Name", "Year", "Parameter_Type"),
  FOREIGN KEY ("WQ_Station_Name") REFERENCES "River_Station" ("WQ_Station_Name"),
  FOREIGN KEY ("Year") REFERENCES "Year_Time" ("Year"),
  CHECK ("Value" IS NULL OR CASE WHEN "Parameter_Type" = 'pH' THEN "Value" BETWEEN 0 AND 14 ELSE "Value" >= 0 END)
);

CREATE TABLE "Forest_Area_Record" (
  "District_Name" TEXT NOT NULL,
  "Fiscal_Start_Year" INTEGER NOT NULL,
  "Fiscal_End_Year" INTEGER NOT NULL,
  "Protected_Area" REAL,
  "Unclassed_State_Forest_FD_Acre" REAL,
  "Unclassed_State_Forest_Admin_Acre" REAL,
  "Reserved_Forest_Section_20_Acre" REAL,
  "Reserved_Forest_Section_4_6_Acre" REAL,
  "Acquired_Vested_Forest" REAL,
  "Total_Forest_FD_Acre" REAL,
  "Total_Forest_Land" REAL,
  PRIMARY KEY ("District_Name", "Fiscal_Start_Year", "Fiscal_End_Year"),
  FOREIGN KEY ("District_Name") REFERENCES "District" ("District_Name"),
  FOREIGN KEY ("Fiscal_Start_Year", "Fiscal_End_Year") REFERENCES "Fiscal_Year" ("Start_Year", "End_Year"),
  CHECK ("Protected_Area" IS NULL OR "Protected_Area" >= 0),
  CHECK ("Unclassed_State_Forest_FD_Acre" IS NULL OR "Unclassed_State_Forest_FD_Acre" >= 0),
  CHECK ("Unclassed_State_Forest_Admin_Acre" IS NULL OR "Unclassed_State_Forest_Admin_Acre" >= 0),
  CHECK ("Reserved_Forest_Section_20_Acre" IS NULL OR "Reserved_Forest_Section_20_Acre" >= 0),
  CHECK ("Reserved_Forest_Section_4_6_Acre" IS NULL OR "Reserved_Forest_Section_4_6_Acre" >= 0),
  CHECK ("Acquired_Vested_Forest" IS NULL OR "Acquired_Vested_Forest" >= 0),
  CHECK ("Total_Forest_FD_Acre" IS NULL OR "Total_Forest_FD_Acre" >= 0),
  CHECK ("Total_Forest_Land" IS NULL OR "Total_Forest_Land" >= 0)
);

CREATE TABLE "Type_Of_Establishments" (
  "Size_Name" TEXT NOT NULL,
  "Start_Year" INTEGER NOT NULL,
  "End_Year" INTEGER NOT NULL,
  "Quantity" INTEGER,
  "Percentage" REAL,
  PRIMARY KEY ("Size_Name", "Start_Year", "End_Year"),
  FOREIGN KEY ("Size_Name") REFERENCES "Size" ("Size_Name"),
  FOREIGN KEY ("Start_Year", "End_Year") REFERENCES "Fiscal_Year" ("Start_Year", "End_Year"),
  CHECK ("Quantity" IS NULL OR "Quantity" >= 0),
  CHECK ("Percentage" IS NULL OR "Percentage" BETWEEN 0 AND 100)
);

CREATE TABLE "Industry_Usage" (
  "Industry_Name" TEXT NOT NULL,
  "Start_Year" INTEGER NOT NULL,
  "End_Year" INTEGER NOT NULL,
  "Quantity" REAL,
  "Percentage" REAL,
  PRIMARY KEY ("Industry_Name", "Start_Year", "End_Year"),
  FOREIGN KEY ("Industry_Name") REFERENCES "Industry_Type" ("Industry_Name"),
  FOREIGN KEY ("Start_Year", "End_Year") REFERENCES "Fiscal_Year" ("Start_Year", "End_Year"),
  CHECK ("Quantity" IS NULL OR "Quantity" >= 0),
  CHECK ("Percentage" IS NULL OR "Percentage" BETWEEN 0 AND 100)
);

CREATE VIEW "Monthly_Climate_Summary" AS
WITH "Monthly_Keys" AS (
  SELECT "Station_Name", "Year", "Month" FROM "Temperature_Record"
  UNION SELECT "Station_Name", "Year", "Month" FROM "Humidity_Record"
  UNION SELECT "Station_Name", "Year", "Month" FROM "Rainfall_Record"
  UNION SELECT "Station_Name", "Year", "Month" FROM "Climatic_Event_Record"
)
SELECT k."Station_Name", k."Year", k."Month",
       MAX(CASE WHEN t."Type" = 'Maximum' THEN t."Temp" END) AS "Maximum_Temperature",
       MAX(CASE WHEN t."Type" = 'Minimum' THEN t."Temp" END) AS "Minimum_Temperature",
       h."Humidity", r."Rainfall", e."Thunderstorm", e."Lightning"
FROM "Monthly_Keys" AS k
LEFT JOIN "Temperature_Record" AS t ON t."Station_Name" = k."Station_Name" AND t."Year" = k."Year" AND t."Month" = k."Month"
LEFT JOIN "Humidity_Record" AS h ON h."Station_Name" = k."Station_Name" AND h."Year" = k."Year" AND h."Month" = k."Month"
LEFT JOIN "Rainfall_Record" AS r ON r."Station_Name" = k."Station_Name" AND r."Year" = k."Year" AND r."Month" = k."Month"
LEFT JOIN "Climatic_Event_Record" AS e ON e."Station_Name" = k."Station_Name" AND e."Year" = k."Year" AND e."Month" = k."Month"
GROUP BY k."Station_Name", k."Year", k."Month", h."Humidity", r."Rainfall", e."Thunderstorm", e."Lightning";

CREATE VIEW "Monthly_Wind_Summary" AS
SELECT "Station_Name", "Year", "Month",
       MAX(CASE WHEN "Type" = 'Maximum' THEN "Wind_Speed" END) AS "Maximum_Wind_Speed",
       MAX(CASE WHEN "Type" = 'Maximum' THEN "Direction" END) AS "Maximum_Wind_Direction",
       MAX(CASE WHEN "Type" = 'Minimum' THEN "Wind_Speed" END) AS "Minimum_Wind_Speed",
       MAX(CASE WHEN "Type" = 'Minimum' THEN "Direction" END) AS "Minimum_Wind_Direction"
FROM "Wind_Record"
GROUP BY "Station_Name", "Year", "Month";
