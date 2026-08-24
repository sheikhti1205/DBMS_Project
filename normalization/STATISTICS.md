# Load Statistics

Every figure below is counted by the extraction program while it reads the source files. No figure is estimated.

## 1. How much each source organisation contributes

Two different figures are given, because they answer two different questions. The first counts values read out of the published files. The second counts rows that survive into the final database. They differ for one stated reason: the Bangladesh Rice Research Institute publishes a reading for every day, and the approved design records climate at month grain, so many daily readings become one row.

| Organisation | Raw blocks read | Values read from the source | Rows offered to the final database |
|---|---|---|---|
| BRRI | 5 | 3252182 | 600166 |
| BBS | 36 | 181600 | 176442 |
| BMD | 20 | 14688 | 14688 |
| **Total** | **62** | **3448470** | **791701** |

## 2. Cells read, kept and missing, per raw block

| Block | Organisation | Sheet | Cells read | Values kept | Missing or unusable |
|---|---|---|---|---|---|
| B01 | BBS | T1.02 | 2520 | 2514 | 6 |
| B02 | BBS | T1.02 | 3360 | 2487 | 873 |
| B03 | BBS | T1.03 | 2520 | 2515 | 5 |
| B04 | BBS | T1.03 | 3360 | 2498 | 862 |
| B05 | BBS | T1.05 | 1680 | 1680 | 0 |
| B06 | BBS | T1.05 | 2100 | 2098 | 2 |
| B07 | BBS | T1.05 | 2100 | 2093 | 7 |
| B08 | BBS | T1.06 | 1728 | 1724 | 4 |
| B09 | BBS | T1.06 | 2100 | 2098 | 2 |
| B10 | BBS | T1.06 | 2100 | 2084 | 16 |
| B11 | BBS | T1.08 | 4200 | 3934 | 266 |
| B12 | BBS | T1.10 | 2448 | 2448 | 0 |
| B13 | BBS | T1.10 | 3408 | 3120 | 288 |
| B14 | BBS | T1.13 | 78120 | 75703 | 2417 |
| B15 | BBS | T1.14 | 31248 | 9352 | 21896 |
| B16 | BBS | T1.14 | 31248 | 18893 | 12355 |
| B17 | BBS | T1.14 | 31248 | 14476 | 16772 |
| B18 | BBS | T1.14 | 31248 | 15582 | 15666 |
| B19 | BBS | T1.14 | 31248 | 4718 | 26530 |
| B20 | BBS | T1.19 | 4200 | 3934 | 266 |
| B21 | BBS | T1.19 a | 4200 | 3925 | 275 |
| B22 | BBS | T1.66 | 1400 | 1350 | 50 |
| B23 | BBS | T1.84 | 727 | 587 | 140 |
| B24 | BBS | T1.84 | 44 | 44 | 0 |
| B25 | BBS | T1.84b | 727 | 250 | 477 |
| B26 | BBS | T1.84c | 727 | 652 | 75 |
| B27 | BBS | T184d | 762 | 40 | 722 |
| B28 | BBS | T1.84e | 729 | 653 | 76 |
| B29 | BBS | T1.85 | 42 | 15 | 27 |
| B30 | BBS | T1.85b | 42 | 15 | 27 |
| B31 | BBS | T1.85c | 42 | 32 | 10 |
| B32 | BBS | T1.85d | 42 | 32 | 10 |
| B33 | BBS | T1.85e | 42 | 32 | 10 |
| B34 | BBS | T1.85f | 42 | 7 | 35 |
| B35 | BBS | T3.14 | 12 | 12 | 0 |
| B36 | BBS | T3.22 | 3 | 3 | 0 |
| B37 | BMD | Table-1 | 816 | 816 | 0 |
| B38 | BMD | Table-2 | 816 | 816 | 0 |
| B39 | BMD | Table-3 | 816 | 816 | 0 |
| B40 | BMD | Table-4 | 816 | 816 | 0 |
| B41 | BMD | Table-5 | 816 | 816 | 0 |
| B42 | BMD | Table-6 | 816 | 816 | 0 |
| B43 | BMD | Table-7 | 816 | 816 | 0 |
| B44 | BMD | Table-8 | 816 | 816 | 0 |
| B45 | BMD | Table-9 | 816 | 816 | 0 |
| B46 | BMD | Table-10 | 816 | 816 | 0 |
| B47 | BMD | Table-11 | 816 | 816 | 0 |
| B48 | BMD | Table-12 | 816 | 816 | 0 |
| B49 | BMD | Table-13 | 816 | 816 | 0 |
| B50 | BMD | Table-14 | 816 | 816 | 0 |
| B51 | BMD | Table-15 | 816 | 816 | 0 |
| B52 | BMD | Table-16 | 816 | 816 | 0 |
| B53 | BMD | Table-17 | 816 | 816 | 0 |
| B54 | BMD | Table-18 | 816 | 816 | 0 |
| B57 | BRRI | BRRI_Daily_Maximum_Temperature | 648954 | 616383 | 32571 |
| B58 | BRRI | BRRI_Daily_Minimum_Temperature | 648954 | 615968 | 32986 |
| B59 | BRRI | BRRI_Daily_Total_Rainfall | 784331 | 754555 | 29776 |
| B60 | BRRI | BRRI_Daily_Average_Humidity | 785106 | 755764 | 29342 |
| B61 | BRRI | BRRI_Daily_Sunshine | 553505 | 509512 | 43993 |
| **Total** | | | **3717305** | **3448470** | **268835** |

## 3. Row counts through the normalization chain

| Stage | Table | Rows |
|---|---|---|
| 1NF | BRRI_Humidity_Daily_1NF | 755740 |
| 1NF | BRRI_Maximum_Temperature_Daily_1NF | 616381 |
| 1NF | BRRI_Minimum_Temperature_Daily_1NF | 615964 |
| 1NF | BRRI_Rainfall_Daily_1NF | 754488 |
| 1NF | Climate_Observation_1NF | 154049 |
| 1NF | Daily_Observation_1NF | 648061 |
| 1NF | Forest_Area_1NF | 1350 |
| 1NF | River_Register_1NF | 405 |
| 1NF | Waste_Water_1NF | 15 |
| 1NF | Water_Quality_1NF | 2352 |
| 2NF | Climate_Observation_2NF | 154049 |
| 2NF | Daily_Observation_2NF | 648061 |
| 2NF | Fiscal_Year_2NF | 5 |
| 2NF | Forest_Area_2NF | 1350 |
| 2NF | Measure_Unit_2NF | 19 |
| 2NF | River_Register_2NF | 405 |
| 2NF | River_Station_2NF | 321 |
| 2NF | Source_Block_2NF | 62 |
| 2NF | Waste_Water_2NF | 15 |
| 2NF | Water_Quality_2NF | 2352 |
| 3NF | Climatic_Event_Record_3NF | 4006 |
| 3NF | Fiscal_Year_3NF | 5 |
| 3NF | Forest_Area_Record_3NF | 175 |
| 3NF | Humidity_Record_3NF | 30820 |
| 3NF | Industry_Usage_3NF | 3 |
| 3NF | Radiation_Record_3NF | 62931 |
| 3NF | Rainfall_Record_3NF | 30795 |
| 3NF | River_Register_3NF | 405 |
| 3NF | River_Station_3NF | 321 |
| 3NF | Sunshine_Record_3NF | 585130 |
| 3NF | Temperature_Record_3NF | 65596 |
| 3NF | Type_Of_Establishments_3NF | 12 |
| 3NF | Water_Quality_3NF | 2352 |
| 3NF | Wind_Record_3NF | 9491 |
| BCNF | Climatic_Event_Record | 4006 |
| BCNF | Day_Time | 23348 |
| BCNF | District | 35 |
| BCNF | Fiscal_Year | 6 |
| BCNF | Forest_Area_Record | 175 |
| BCNF | Humidity_Record | 25350 |
| BCNF | Industry_Type | 1 |
| BCNF | Industry_Usage | 3 |
| BCNF | Month_Time | 924 |
| BCNF | Radiation_Record | 62931 |
| BCNF | Rainfall_Record | 25453 |
| BCNF | River | 417 |
| BCNF | River_Station | 321 |
| BCNF | Size | 4 |
| BCNF | Station | 56 |
| BCNF | Sunshine_Record | 533140 |
| BCNF | Temperature_Record | 42295 |
| BCNF | Type_Of_Establishments | 12 |
| BCNF | Water_Quality | 2327 |
| BCNF | Wind_Record | 9443 |
| BCNF | Year_Time | 77 |

## 4. Final relation sizes

| Relation | Primary key | Attributes | Rows |
|---|---|---|---|
| Climatic_Event_Record | (Station_Name, Year, Month) | 5 | 4006 |
| Day_Time | (Year, Month, Day) | 3 | 23348 |
| District | District_Name | 1 | 35 |
| Fiscal_Year | (Start_Year, End_Year) | 2 | 6 |
| Forest_Area_Record | (District_Name, Fiscal_Start_Year, Fiscal_End_Year) | 11 | 175 |
| Humidity_Record | (Station_Name, Year, Month) | 4 | 25350 |
| Industry_Type | Industry_Name | 1 | 1 |
| Industry_Usage | (Industry_Name, Start_Year, End_Year) | 5 | 3 |
| Month_Time | (Year, Month) | 2 | 924 |
| Radiation_Record | (Station_Name, Year, Month, Day, Sample_No) | 6 | 62931 |
| Rainfall_Record | (Station_Name, Year, Month) | 4 | 25453 |
| River | River_Name | 1 | 417 |
| River_Station | WQ_Station_Name | 2 | 321 |
| Size | Size_Name | 1 | 4 |
| Station | Station_Name | 2 | 56 |
| Sunshine_Record | (Station_Name, Year, Month, Day) | 5 | 533140 |
| Temperature_Record | (Station_Name, Year, Month, Type) | 5 | 42295 |
| Type_Of_Establishments | (Size_Name, Start_Year, End_Year) | 5 | 12 |
| Water_Quality | (WQ_Station_Name, Year, Parameter_Type) | 4 | 2327 |
| Wind_Record | (Station_Name, Year, Month, Type) | 6 | 9443 |
| Year_Time | Year | 1 | 77 |
| **Total** | | | **730324** |

## 5. Distinct key values in the loaded database

| Reference set | Distinct values |
|---|---|
| Station | 56 |
| District | 35 |
| River | 417 |
| River_Station | 321 |
| Year_Time | 77 |
| Month_Time | 924 |
| Day_Time | 23348 |
| Fiscal_Year | 6 |

The loaded database covers the years 1948 to 2024.
