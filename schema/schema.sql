PRAGMA foreign_keys = ON;

CREATE TABLE "Year_Time" (
  "Year" INTEGER NOT NULL,
  PRIMARY KEY ("Year")
);

CREATE TABLE "Month_Time" (
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  PRIMARY KEY ("Year", "Month"),
  FOREIGN KEY ("Year") REFERENCES "Year_Time" ("Year")
);

CREATE TABLE "Day_Time" (
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Day" INTEGER NOT NULL,
  PRIMARY KEY ("Year", "Month", "Day"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month")
);

CREATE TABLE "Fiscal_Year" (
  "Start_Year" INTEGER NOT NULL,
  "End_Year" INTEGER NOT NULL,
  PRIMARY KEY ("Start_Year", "End_Year"),
  FOREIGN KEY ("Start_Year") REFERENCES "Year_Time" ("Year"),
  FOREIGN KEY ("End_Year") REFERENCES "Year_Time" ("Year")
);

CREATE TABLE "Station" (
  "Station_Name" TEXT NOT NULL,
  PRIMARY KEY ("Station_Name")
);

CREATE TABLE "District" (
  "District_Name" TEXT NOT NULL,
  PRIMARY KEY ("District_Name")
);

CREATE TABLE "River" (
  "River_Name" TEXT NOT NULL,
  PRIMARY KEY ("River_Name")
);

CREATE TABLE "River_Station" (
  "WQ_Station_Name" TEXT NOT NULL,
  "River_Name" TEXT,
  PRIMARY KEY ("WQ_Station_Name"),
  FOREIGN KEY ("River_Name") REFERENCES "River" ("River_Name")
);

CREATE TABLE "Size" (
  "Size_Name" TEXT NOT NULL,
  PRIMARY KEY ("Size_Name")
);

CREATE TABLE "Industrial_Type" (
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
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month")
);

CREATE TABLE "Humidity_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Humidity" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month")
);

CREATE TABLE "Rainfall_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Rainfall" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month")
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
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month")
);

CREATE TABLE "Climatic_Event_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Thunderstorm" REAL,
  "Lightning" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month") REFERENCES "Month_Time" ("Year", "Month")
);

CREATE TABLE "Sunshine_Record" (
  "Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Month" INTEGER NOT NULL,
  "Day" INTEGER NOT NULL,
  "Sunshine_Hours" REAL,
  PRIMARY KEY ("Station_Name", "Year", "Month", "Day"),
  FOREIGN KEY ("Station_Name") REFERENCES "Station" ("Station_Name"),
  FOREIGN KEY ("Year", "Month", "Day") REFERENCES "Day_Time" ("Year", "Month", "Day")
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
  FOREIGN KEY ("Year", "Month", "Day") REFERENCES "Day_Time" ("Year", "Month", "Day")
);

CREATE TABLE "Water_Quality" (
  "WQ_Station_Name" TEXT NOT NULL,
  "Year" INTEGER NOT NULL,
  "Parameter_Type" TEXT NOT NULL,
  "Value" REAL,
  PRIMARY KEY ("WQ_Station_Name", "Year", "Parameter_Type"),
  FOREIGN KEY ("WQ_Station_Name") REFERENCES "River_Station" ("WQ_Station_Name"),
  FOREIGN KEY ("Year") REFERENCES "Year_Time" ("Year")
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
  FOREIGN KEY ("Fiscal_Start_Year", "Fiscal_End_Year") REFERENCES "Fiscal_Year" ("Start_Year", "End_Year")
);

CREATE TABLE "Type_Of_Establishments" (
  "Size_Name" TEXT NOT NULL,
  "Start_Year" INTEGER NOT NULL,
  "End_Year" INTEGER NOT NULL,
  "Quantity" INTEGER,
  "Percentage" REAL,
  PRIMARY KEY ("Size_Name", "Start_Year", "End_Year"),
  FOREIGN KEY ("Size_Name") REFERENCES "Size" ("Size_Name"),
  FOREIGN KEY ("Start_Year", "End_Year") REFERENCES "Fiscal_Year" ("Start_Year", "End_Year")
);

CREATE TABLE "Industry_Usage" (
  "Industry_Name" TEXT NOT NULL,
  "Start_Year" INTEGER NOT NULL,
  "End_Year" INTEGER NOT NULL,
  "Produced_Waste_Water" REAL,
  "Reused_Waste_Water" REAL,
  PRIMARY KEY ("Industry_Name", "Start_Year", "End_Year"),
  FOREIGN KEY ("Industry_Name") REFERENCES "Industrial_Type" ("Industry_Name"),
  FOREIGN KEY ("Start_Year", "End_Year") REFERENCES "Fiscal_Year" ("Start_Year", "End_Year")
);

CREATE VIEW "Industry_Usage_With_Rate" AS
SELECT "Industry_Name", "Start_Year", "End_Year",
       "Produced_Waste_Water", "Reused_Waste_Water",
       CASE WHEN "Produced_Waste_Water" IS NULL OR "Produced_Waste_Water" = 0
            THEN NULL
            ELSE 100.0 * "Reused_Waste_Water" / "Produced_Waste_Water"
       END AS "Reuse_Percentage"
FROM "Industry_Usage";
