# Data Quality Log

Every problem the extraction program meets in the source files is counted here. Nothing is silently corrected: a repair is recorded as a repair, and a value that cannot be repaired is left empty rather than replaced with a zero.

## 1. Problems found, by class

| Problem found in the source | Times | Examples |
|---|---|---|
| Missing-data sentinel (****) | 75230 | B01 Bogura 2013-04; B01 Bogura 2013 annual; B01 Maijdi Court 2014-02; B01 Maijdi Court 2014 annual; B01 Sandwip 2012-12; B01 Sandwip 2012 annual |
| Missing-data sentinel (***) | 29547 | B02 Teknaf 2024-06; B02 Teknaf 2024-07; B02 Teknaf 2024-08; B02 Teknaf 2024-09; B02 Teknaf 2024-10; B02 Teknaf 2024-11 |
| Numeric value stored as text | 15078 | 25.4 -> B37 Dhaka 1995-01 max; 11.3 -> B37 Dhaka 1995-01 min; 28.0 -> B37 Dhaka 1995-02 max; 15.7 -> B37 Dhaka 1995-02 min; 33.8 -> B37 Dhaka 1995-03 max; 19.3 -> B37 Dhaka 1995-03 min |
| Missing-data sentinel (**) | 8383 | B11 Dinajpur 2024-08 spd; B11 Dinajpur 2024-08 dir; B11 Dinajpur 2024-09 spd; B11 Dinajpur 2024-09 dir; B11 Dinajpur 2024-10 spd; B11 Dinajpur 2024-10 dir |
| Station name published entirely in lower case | 1333 | chuadanga -> Chuadanga; rajshahi -> Rajshahi; rangpur -> Rangpur; rangamati -> Rangamati; 1.0 -> 1.0 |
| Rainfall trace sentinel 'T' substituted with 0 | 919 | B59 Ambagan (Ctg) 2023-07-08; B59 Ambagan (Ctg) 2023-07-15; B59 Ambagan (Ctg) 2023-07-22; B59 Ambagan (Ctg) 2023-08-11; B59 Ambagan (Ctg) 2023-08-20; B59 Ambagan (Ctg) 2023-08-31 |
| Month aggregated from fewer than 25 daily readings | 912 | Max_Temp Barisal 1971-03: 24 days; Max_Temp Barisal 1971-04: 11 days; Max_Temp Barisal 1971-08: 23 days; Max_Temp Barisal 1972-12: 22 days; Max_Temp Barisal 1987-06: 24 days; Max_Temp Bhola 1970-07: 18 days |
| Missing-data sentinel (asterisks) | 492 | B06 Chuadanga 2019 annual; B06 Mongla 2019 annual; B60 Barisal 1951-03-09; B60 Barisal 1951-04-09; B60 Barisal 1958-03-09; B60 Barisal 1964-01-09 |
| Missing-data sentinel (#DIV/0!) | 295 | B60 Aricha 2023-10-26; B60 Badalgachi 2021-02-29; B60 Badalgachi 2021-02-30; B60 Badalgachi 2021-03-30; B60 Badalgachi 2021-06-07; B60 Badalgachi 2021-06-08 |
| Day number beyond the length of the month | 239 | 2019-02 day 29 (B15 Bogura); 2019-02 day 30 (B15 Bogura); 2019-02 day 31 (B15 Bogura); 2019-04 day 31 (B15 Bogura); 2021-02 day 29 (B16 Dinajpur); 2021-02 day 30 (B16 Dinajpur) |
| Textual nil / Nill in place of zero | 224 | Nill -> B61 Gazipur 2000-05-27; Nill -> B61 Gazipur 2000-05-28; Nill -> B61 Gazipur 2000-07-18; Nill -> B61 Gazipur 2000-07-19; Nill -> B61 Gazipur 2000-09-17; Nill -> B61 Gazipur 2000-09-18 |
| Value with trailing footnote marker | 71 | 94 1 -> B60 Ambagan (Ctg) 2018-06-09; 86 * -> B60 Barisal 1965-05-09; 80 * -> B60 Chandpur 1968-10-09; 97 1 -> B60 Chandpur 1969-07-09; 100 * -> B60 Chandpur 1973-12-09; 89 1 -> B60 Chandpur 1975-11-09 |
| Station latitude/longitude embedded in a label row | 69 | Dinajpur Lat.25Deg.39Mts.N Long.88Deg.41Mts.E; Rangpur Lat.25Deg.44Mts.N Long.89Deg.14Mts.E; Rajshahi Lat.24Deg.22Mts.N Long.88Deg.42Mts.E; Bogura Lat.24Deg.51Mts.N Long.89Deg.22Mts.E; Mymensingh Lat.24Deg.43Mts.N Long.9 |
| Missing-data sentinel (ND) | 55 | B29 Karnaphuli Mohona 2022 Biochemical Oxygen Demand; B29 Karnaphuli Mohona 2023 Biochemical Oxygen Demand; B29 Karnaphuli Mohona 2024 Biochemical Oxygen Demand; B29 1 km straight from Patenga Sea Beach 2022 Biochemical  |
| River or lake name published by BBS that is absent from the BWDB river register | 47 | Chaktai Khal; Dhanmondi Lake; Hatir Jhill Lake; Dlolaikhal; Krishna Khal; Moyuri River |
| Sunshine value outside the plausible range 0 to 14, because the longest day at this latitude is close to 13 hours and 30 minutes, so a day cannot hold more than 14 hours of bright sunshine | 33 | B14 Dhaka 2024-11-18 = 14.6; B14 Chuadanga 2024-7-18 = 20.2; B14 Chuadanga 2024-10-7 = 17.9; B14 Chuadanga 2024-10-14 = 17; B14 Patuakhali 2024-9-30 = 17.3; B14 Ambagan (Ctg) 2023-1-13 = 19.8 |
| Missing-data sentinel (-) | 24 | B29 Joramtol Shipyard Area 2019 Biochemical Oxygen Demand; B29 Joramtol Shipyard Area 2020 Biochemical Oxygen Demand; B29 Joramtol Shipyard Area 2021 Biochemical Oxygen Demand; B29 Joramtol Shipyard Area 2022 Biochemical |
| Thousands separator written as a decimal point | 22 | 65.173.21 -> 65173.21 (B22 Gazipur 2019-20 Total_Forest_Land); 65.173.21 -> 65173.21 (B22 Gazipur 2020-21 Total_Forest_Land); 65.173.21 -> 65173.21 (B22 Gazipur 2021-22 Total_Forest_Land); 65.173.21 -> 65173.21 (B22 Gazi |
| Sub-Division value stored with its characters reversed | 20 | allimuK -> Kumilla; akahD -> Dhaka; rupdiraF -> Faridpur |
| Groundwater well before the first district label | 15 | Table-3 well SY005; Table-3 well SY022; Table-3 well SY079; Table-3 well SY002; Table-5 well DH098; Table-5 well DH067 |
| Month name misspelled in source ('Feburary') | 14 | feburary |
| Unparseable measurement cell | 11 | 'Data is not availaable/ Did not generate By BMD' -> B15 Bogura 2019-11-05 h07; 'Data is not availaable/ Did not generate By BMD' -> B15 Bogura 2019-12-04 h06; 'Instrument Out of Date' -> B18 Satkhira 2021-09-07 h05; 'In |
| Wind Direction value outside the plausible range 0 to 360, because a compass bearing lies in 0 to 360 | 11 | B11 Mymensingh 2022-11-Minimum direction = 9990; B11 Mymensingh 2022-12-Minimum direction = 9990; B11 Mymensingh 2023-2-Minimum direction = 9990; B11 Sitakunda 2020-12-Minimum direction = 9990; B11 Sitakunda 2021-10-Mini |
| Sentinel 999 = No Data | 9 | B11 Mymensingh 2022-11 spd; B11 Mymensingh 2022-12 spd; B11 Mymensingh 2023-02 spd; B11 Sitakunda 2020-12 spd; B11 Sitakunda 2021-10 spd; B11 Sitakunda 2021-11 spd |
| Water quality station listed under more than one river | 9 | Pagla -> ['Buriganga River', 'Dlolaikhal']; Karnafully Mohona -> ['Chaktai Khal', 'Karnaphuli River']; 1km Straight from patenga sea beach -> ['Chaktai Khal', 'Karnaphuli River']; Patenga charpara -> ['Chaktai Khal', 'Ka |
| Category label glued to its numeric value | 8 | 0. 00 -> B22 Thakurgaon 2021-22 Acquired_Vested_Forest; Plastic 4193 -> B34 Karnaphuli Mohona 2019 Plastic and Marine Debris; Foamed Plastic 860 -> B34 1 km straight from Patenga Sea Beach 2019 Plastic and Marine Debris; |
| Header or note text found in a station column | 7 | Note: **** Means Missing Data.; Note: *** Means Missing Data/ Data Not Available; Source : Bangladesh Meteorological Department (BMD); Daily Total Sun Shine Hours by Station, 2019-2024; Stations |
| Missing-data sentinel (N/A) | 7 | B15 Bogura 2021-01-06 h06; B15 Bogura 2021-02-07 h07; B15 Bogura 2021-03-08 h04; B17 Dhaka 2021-11-06 h04; B17 Dhaka 2021-12-09 h05; B18 Satkhira 2021-01-12 h04 |
| Missing-data sentinel (*) | 6 | B58 Gazipur 2004-02-30; B58 Gazipur 2004-02-31; B59 Gazipur 2001-03-05; B59 Gazipur 2001-04-28; B59 Gazipur 2005-02-19; B59 Gazipur 2005-08-09 |
| Doubled decimal point repaired | 3 | 27..4 -> B58 Bogura 2021-06-25; 26..2 -> B58 Jessore 2023-09-20; 2..4 -> B59 Gazipur 2022-05-01 |
| Missing-data sentinel (///) | 3 | B58 Tangail 2021-01-01; B58 Tangail 2021-01-02; B58 Tangail 2021-01-03 |
| BMD Sunshine.xls carries Station ID 0.0 on every row and no station name, so its rows cannot be attached to a Station | 2 | Climate : 12 data rows unattachable; Climate Leap year February: 1 data rows unattachable |
| Humidity value outside the plausible range 0 to 100, because relative humidity is a percentage and cannot exceed 100 | 2 | B60 Gazipur 2007-5 = 189.6; B60 Patuakhali 2021-6 = 104.35 |
| Radiation hour range present in source is only 0..13, not the 0..23 the schema anticipates | 1 | hours observed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] |
| Column number legend row found in a district column | 1 | 2.0 |
| Aggregate "Total" row inside the establishment block | 1 | T3.14 row 6 |
| Source sheet T3.22 publishes only one category row, so Industrial_Type is loaded with a single industry and Industry_Usage with one row per fiscal year | 1 | 1 row(s) present |
| T3.22 labels reused waste water as a percentage although its values are outside the percentage range and the table title states thousand litres | 1 | The published values are preserved as reused waste water; a separate database view calculates the reuse rate for review |
| BRRI daily readings aggregated to month grain to match the approved schema | 1 | 90737 station-months formed |
| Rainfall value outside the plausible range 0 to 3000, because the wettest recorded month in Bangladesh is below 3000 millimetres | 1 | B59 Sandwip 2001-6 = 3001 |
| Marine monitoring point stands in the sea, so the source names no river. The water body is recorded as Bay of Bengal so the reading keeps a valid parent row | 1 | 7 stations: 1 km straight from CEPZ, 1 km straight from Patenga Sea Beach, Joramtol Shipyard Area, Karnaphuli Mohona |
| The approved diagram has no groundwater entity, so the wells reconciled at Third Normal Form have no relation to load into | 1 | 196 wells from 37 districts stop at Third Normal Form |
| Both waste relations are keyed by fiscal year in the approved diagram, so every published year loads rather than only the latest | 1 | Type_Of_Establishments 12 rows over 3 fiscal years; Industry_Usage 3 rows over 3 |
| Every water quality station name is unique in River_Station, so WQ_Station_Name is the relation primary key and the single column foreign key from Water_Quality is valid | 1 | 323 stations verified |

Total problem occurrences recorded: **133111** across **44** distinct classes.

## 2. Station names reconciled

The same weather station is spelled differently by different organisations, and sometimes differently within one file. Each variant is mapped to one canonical name so that the primary key of every climate relation is stable.

| Name as published | Canonical name used |
|---|---|
| Ambagan | Ambagan (Ctg) |
| Ambagan(Ctg | Ambagan (Ctg) |
| Ambagan(Ctg) | Ambagan (Ctg) |
| Ambagan_Ctg | Ambagan (Ctg) |
| Bogra | Bogura |
| Chattogram | Chittagong |
| Chi(Patanga) | Chittagong (Patenga) |
| Cox's | Cox's Bazar |
| Cox'sBazar | Cox's Bazar |
| Cox's_Bazar | Cox's Bazar |
| Cox'sbazar | Cox's Bazar |
| Cox`s Bazar | Cox's Bazar |
| Ctg(Ambagan) | Ambagan (Ctg) |
| Ctg(Patenga) | Chittagong (Patenga) |
| Ctg. (Ambagan) | Ambagan (Ctg) |
| Ctg. (Patanga) | Chittagong (Patenga) |
| Hatia | Hatiya |
| Ishardi | Ishurdi |
| Jashore | Jessore |
| Khapupara | Khepupara |
| M.Court | Maijdi Court |
| M.court | Maijdi Court |
| M_Court | Maijdi Court |
| Maijdicourt | Maijdi Court |
| Srimongal | Srimangal |
| Sydpur | Sayedpur |
| Syedpur | Sayedpur |
| chi(Ambagan) | Ambagan (Ctg) |
| chuadanga | Chuadanga |
| rajshahi | Rajshahi |
| rangamati | Rangamati |
| rangpur | Rangpur |
| sydpur | Sayedpur |

## 3. District names reconciled

| Name as published | Canonical name used |
|---|---|
| Chittaganj | Chattogram |
| Cumilla | Kumilla |
| Hobigonj | Habiganj |
| Khagrachari | Khagrachhari |
| Maulavibazar | Moulvi Bazar |
| Mymenshingh | Mymensingh |
| Perojpur | Pirojpur |
| Satkhiar | Satkhira |
| Sunamgonj | Sunamganj |

## 4. River names reconciled against the BWDB register

| Name as published by BBS | Name in the BWDB register |
|---|---|
| Balu River | Balu |
| Bhairab River | Bhairab (Bagerhat) |
| Bhrammaputra River | Old Brahmaputra |
| Buriganga River | Buriganga |
| Dhalaswary River | Dhaleshwari |
| Gorai River | Garai |
| Halda River | Halda |
| Jamuna River | Jamuna (Panchagarh) |
| Kaligonga River | Kaliganga (Pirojpur) |
| Karnaphuli River | Karnafuli |
| Khakshiali River | Kakshiali |
| Kirtonkhola River | Kirtankhola |
| Korotoa River | Karatoa (Nilphamari) |
| Kushiara River | Kushiyara |
| Lohalia River | Lohalia |
| Mathavanga River | Mathabhaga |
| Meghna River | Meghna (upper) |
| Modhumoti River | Madhumati |
| Padma River | Padma |
| Pashur River | Pashur |
| Rupsha River | Rupsa (Khulna) |
| Shitalakhya River | Shetalakhya |
| Sugandha River | Sugandha |
| Surma River | Surma |
| Turagh River | Turag |

## 5. Text found in a station column and dropped

| Value found | Times |
|---|---|
| Note: *** Means Missing Data/ Data Not Available | 2 |
| Source : Bangladesh Meteorological Department (BMD) | 2 |
| Note: **** Means Missing Data. | 1 |
| Daily Total Sun Shine Hours by Station, 2019-2024 | 1 |
| Stations | 1 |

## 6. Primary key conflicts between organisations

Where two organisations publish a different value for the same primary key, the key forbids both. The value from the higher precedence source is kept and the rejected value is recorded here, because a discarded measurement must remain visible.

Precedence used: Bangladesh Bureau of Statistics before Bangladesh Meteorological Department, Bangladesh Meteorological Department before Bangladesh Rice Research Institute.

### 6.1 Summary, and why the two kinds of conflict are separated

Most conflicts are the two organisations rounding the same reading to a different number of decimal places. A conflict is classed as rounding when the two figures agree to within the tolerance stated for the relation, and as substantive otherwise. Only the substantive conflicts mean the two organisations disagree about what was measured.

| Relation | Tolerance treated as rounding | Precedence applied | Rounding | Substantive | Total |
|---|---|---|---|---|---|
| Humidity_Record | 0.5 | BBS over BRRI | 2026 | 3255 | 5281 |
| Rainfall_Record | 0.5 | BBS over BRRI | 0 | 488 | 488 |
| Sunshine_Record | 0.1 | BBS over BRRI | 148 | 8231 | 8379 |
| Temperature_Record | 0.1 | BBS over BMD | 178 | 956 | 1134 |
| Temperature_Record | 0.1 | BBS over BRRI | 8044 | 272 | 8316 |
| Temperature_Record | 0.1 | BMD over BRRI | 11114 | 412 | 11526 |
| Water_Quality | 0.05 | BBS over BBS | 9 | 1 | 10 |
| **Total** | | | **21519** | **13615** | **35134** |

### 6.2 Substantive conflicts

There are **13615** substantive conflicts. The largest are listed below.

| Relation | Key | Source kept | Value kept | Source rejected | Value rejected | Difference |
|---|---|---|---|---|---|---|
| Rainfall_Record | Teknaf | 2020 | 8 | BBS | 1177.0 | BRRI | 0.0 | 1177.00 |
| Rainfall_Record | Teknaf | 2023 | 8 | BBS | 0.0 | BRRI | 1164.0 | 1164.00 |
| Rainfall_Record | Teknaf | 2020 | 7 | BBS | 911.0 | BRRI | 0.0 | 911.00 |
| Rainfall_Record | Teknaf | 2020 | 6 | BBS | 636.0 | BRRI | 0.0 | 636.00 |
| Rainfall_Record | Teknaf | 2020 | 9 | BBS | 570.0 | BRRI | 0.0 | 570.00 |
| Rainfall_Record | Teknaf | 2023 | 10 | BBS | 0.0 | BRRI | 283.0 | 283.00 |
| Rainfall_Record | Madaripur | 2020 | 7 | BBS | 273.0 | BRRI | 0.0 | 273.00 |
| Rainfall_Record | Comilla | 2021 | 7 | BBS | 636.0 | BRRI | 365.0 | 271.00 |
| Rainfall_Record | Sitakunda | 2023 | 8 | BBS | 1249.0 | BRRI | 991.0 | 258.00 |
| Rainfall_Record | Madaripur | 2020 | 6 | BBS | 250.0 | BRRI | 0.0 | 250.00 |
| Rainfall_Record | Madaripur | 2020 | 8 | BBS | 247.0 | BRRI | 0.0 | 247.00 |
| Rainfall_Record | Teknaf | 2023 | 9 | BBS | 0.0 | BRRI | 239.0 | 239.00 |
| Rainfall_Record | Hatiya | 2021 | 6 | BBS | 953.0 | BRRI | 1174.0 | 221.00 |
| Rainfall_Record | Teknaf | 2020 | 10 | BBS | 195.0 | BRRI | 0.0 | 195.00 |
| Rainfall_Record | Madaripur | 2020 | 9 | BBS | 194.0 | BRRI | 0.0 | 194.00 |
| Rainfall_Record | Comilla | 2021 | 6 | BBS | 258.0 | BRRI | 439.0 | 181.00 |
| Rainfall_Record | Sandwip | 2021 | 8 | BBS | 894.0 | BRRI | 713.0 | 181.00 |
| Rainfall_Record | Madaripur | 2020 | 10 | BBS | 133.0 | BRRI | 0.0 | 133.00 |
| Rainfall_Record | Sitakunda | 2021 | 7 | BBS | 716.0 | BRRI | 587.0 | 129.00 |
| Rainfall_Record | Cox's Bazar | 2023 | 10 | BBS | 317.0 | BRRI | 209.0 | 108.00 |
| Rainfall_Record | Sylhet | 2023 | 7 | BBS | 1062.0 | BRRI | 962.0 | 100.00 |
| Rainfall_Record | Teknaf | 2020 | 11 | BBS | 98.0 | BRRI | 0.0 | 98.00 |
| Rainfall_Record | Jessore | 2021 | 4 | BBS | 99.0 | BRRI | 4.0 | 95.00 |
| Rainfall_Record | Kutubdia | 2021 | 9 | BBS | 228.0 | BRRI | 133.0 | 95.00 |
| Rainfall_Record | Sandwip | 2023 | 10 | BBS | 259.0 | BRRI | 167.0 | 92.00 |
| Rainfall_Record | Dhaka | 2023 | 6 | BBS | 363.0 | BRRI | 454.0 | 91.00 |
| Rainfall_Record | Hatiya | 2023 | 8 | BBS | 846.0 | BRRI | 757.0 | 89.00 |
| Rainfall_Record | Feni | 2021 | 6 | BBS | 530.0 | BRRI | 618.0 | 88.00 |
| Rainfall_Record | Faridpur | 2023 | 4 | BBS | 118.0 | BRRI | 32.0 | 86.00 |
| Rainfall_Record | Kutubdia | 2021 | 6 | BBS | 816.0 | BRRI | 902.0 | 86.00 |
| Rainfall_Record | Sitakunda | 2023 | 6 | BBS | 473.0 | BRRI | 387.0 | 86.00 |
| Rainfall_Record | Sylhet | 2023 | 10 | BBS | 691.0 | BRRI | 776.0 | 85.00 |
| Rainfall_Record | Dhaka | 2023 | 7 | BBS | 244.0 | BRRI | 160.0 | 84.00 |
| Rainfall_Record | Sylhet | 2023 | 6 | BBS | 1267.0 | BRRI | 1351.0 | 84.00 |
| Rainfall_Record | Maijdi Court | 2021 | 7 | BBS | 551.0 | BRRI | 468.0 | 83.00 |
| Rainfall_Record | Teknaf | 2023 | 11 | BBS | 0.0 | BRRI | 83.0 | 83.00 |
| Rainfall_Record | Kutubdia | 2021 | 8 | BBS | 893.0 | BRRI | 973.0 | 80.00 |
| Rainfall_Record | Patuakhali | 2021 | 8 | BBS | 447.0 | BRRI | 367.0 | 80.00 |
| Rainfall_Record | Maijdi Court | 2021 | 6 | BBS | 639.0 | BRRI | 717.0 | 78.00 |
| Rainfall_Record | Madaripur | 2023 | 3 | BBS | 117.0 | BRRI | 195.0 | 78.00 |
| Rainfall_Record | Patuakhali | 2021 | 6 | BBS | 541.0 | BRRI | 619.0 | 78.00 |
| Rainfall_Record | Cox's Bazar | 2021 | 6 | BBS | 731.0 | BRRI | 808.0 | 77.00 |
| Rainfall_Record | Madaripur | 2023 | 4 | BBS | 122.0 | BRRI | 45.0 | 77.00 |
| Rainfall_Record | Madaripur | 2021 | 7 | BBS | 357.0 | BRRI | 282.0 | 75.00 |
| Rainfall_Record | Mymensingh | 2023 | 7 | BBS | 348.0 | BRRI | 274.0 | 74.00 |
| Rainfall_Record | Comilla | 2023 | 6 | BBS | 514.0 | BRRI | 586.0 | 72.00 |
| Rainfall_Record | Mymensingh | 2023 | 6 | BBS | 261.0 | BRRI | 333.0 | 72.00 |
| Rainfall_Record | Dinajpur | 2023 | 7 | BBS | 356.0 | BRRI | 285.0 | 71.00 |
| Rainfall_Record | Feni | 2021 | 7 | BBS | 792.0 | BRRI | 721.0 | 71.00 |
| Rainfall_Record | Rangamati | 2021 | 7 | BBS | 478.0 | BRRI | 407.0 | 71.00 |
| Rainfall_Record | Hatiya | 2021 | 7 | BBS | 795.0 | BRRI | 725.0 | 70.00 |
| Rainfall_Record | Mymensingh | 2021 | 8 | BBS | 504.0 | BRRI | 435.0 | 69.00 |
| Rainfall_Record | Jessore | 2023 | 6 | BBS | 162.0 | BRRI | 230.0 | 68.00 |
| Rainfall_Record | Maijdi Court | 2023 | 8 | BBS | 593.0 | BRRI | 525.0 | 68.00 |
| Rainfall_Record | Sandwip | 2021 | 7 | BBS | 866.0 | BRRI | 798.0 | 68.00 |
| Rainfall_Record | Satkhira | 2023 | 8 | BBS | 427.0 | BRRI | 359.0 | 68.00 |
| Rainfall_Record | Bhola | 2023 | 6 | BBS | 299.0 | BRRI | 366.0 | 67.00 |
| Rainfall_Record | Patuakhali | 2021 | 9 | BBS | 296.0 | BRRI | 363.0 | 67.00 |
| Rainfall_Record | Sitakunda | 2021 | 10 | BBS | 196.0 | BRRI | 129.0 | 67.00 |
| Rainfall_Record | Chandpur | 2023 | 8 | BBS | 596.0 | BRRI | 530.0 | 66.00 |
| Rainfall_Record | Hatiya | 2021 | 10 | BBS | 169.0 | BRRI | 104.0 | 65.00 |
| Rainfall_Record | Teknaf | 2021 | 7 | BBS | 1068.0 | BRRI | 1003.0 | 65.00 |
| Rainfall_Record | Barisal | 2021 | 6 | BBS | 404.0 | BRRI | 340.0 | 64.00 |
| Rainfall_Record | Maijdi Court | 2023 | 7 | BBS | 177.0 | BRRI | 241.0 | 64.00 |
| Rainfall_Record | Rangamati | 2021 | 6 | BBS | 375.0 | BRRI | 438.0 | 63.00 |
| Rainfall_Record | Srimangal | 2021 | 7 | BBS | 295.0 | BRRI | 233.0 | 62.00 |
| Rainfall_Record | Teknaf | 2021 | 8 | BBS | 703.0 | BRRI | 641.0 | 62.00 |
| Rainfall_Record | Kutubdia | 2021 | 7 | BBS | 1145.0 | BRRI | 1084.0 | 61.00 |
| Rainfall_Record | Dinajpur | 2023 | 6 | BBS | 199.0 | BRRI | 259.0 | 60.00 |
| Rainfall_Record | Ambagan (Ctg) | 2023 | 8 | BBS | 1120.0 | BRRI | 1061.0 | 59.00 |
| Rainfall_Record | Cox's Bazar | 2021 | 8 | BBS | 995.0 | BRRI | 936.0 | 59.00 |
| Rainfall_Record | Feni | 2021 | 8 | BBS | 439.0 | BRRI | 382.0 | 57.00 |
| Rainfall_Record | Feni | 2023 | 10 | BBS | 173.0 | BRRI | 116.0 | 57.00 |
| Rainfall_Record | Chandpur | 2023 | 6 | BBS | 167.0 | BRRI | 223.0 | 56.00 |
| Rainfall_Record | Srimangal | 2021 | 6 | BBS | 172.0 | BRRI | 228.0 | 56.00 |
| Rainfall_Record | Teknaf | 2023 | 6 | BBS | 381.0 | BRRI | 325.0 | 56.00 |
| Rainfall_Record | Mongla | 2023 | 10 | BBS | 265.0 | BRRI | 210.0 | 55.00 |
| Rainfall_Record | Satkhira | 2023 | 7 | BBS | 173.0 | BRRI | 228.0 | 55.00 |
| Rainfall_Record | Comilla | 2023 | 7 | BBS | 226.0 | BRRI | 172.0 | 54.00 |
| Rainfall_Record | Feni | 2023 | 6 | BBS | 434.0 | BRRI | 488.0 | 54.00 |

The complete list of all **35134** conflicts, rounding and substantive together, is in `csv/BCNF/_Key_Conflicts.csv`.

## 7. Identical duplicates removed

These are rows where two sources publish the same value for the same key. Nothing is lost when the duplicate is dropped.

| Relation | Identical duplicate rows dropped |
|---|---|
| Sunshine_Record | 43611 |
| Rainfall_Record | 4854 |
| Temperature_Record | 2327 |
| Humidity_Record | 189 |
| Wind_Record | 48 |
| Water_Quality | 15 |

## 8. Raw blocks that could not be loaded at all

| Block | Source | Rows in the block | Reason it cannot be loaded |
|---|---|---|---|
| B55 | BMD Sunshine.xls / Climate  | 12 | Station identifier is 0.0 on every row and no station name column exists. Sunshine_Record has Station_Name in its primary key, so no row can be inserted without inventing a station. |
| B56 | BMD Sunshine.xls / Climate Leap year February | 1 | Station identifier is 0.0 on every row and no station name column exists. Sunshine_Record has Station_Name in its primary key, so no row can be inserted without inventing a station. |

## 9. Constraint verification on the loaded database

The two constraints that a relational database enforces are checked against the loaded tables. Both are reported here as measured results, not as assertions.

| Constraint checked | Relations checked | Violations found |
|---|---|---|
| Primary key holds no duplicate value | 21 | 0 |
| Every foreign key value exists in the parent relation | 27 | 0 |

No violation of any kind is found. Every relation loads with a unique primary key, and every foreign key value has a matching parent row.
