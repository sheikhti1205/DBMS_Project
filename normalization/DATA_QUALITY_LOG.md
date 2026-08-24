# Data Quality Log

Every problem the extraction program meets in the source files is counted here. Nothing is silently corrected: a repair is recorded as a repair, and a record that cannot be repaired is quarantined rather than replaced with an invented value.

## 1. Problems found, by class

| Problem found in the source | Times | Examples |
|---|---|---|
| Missing-data sentinel (****) | 75230 | B01 Bogura 2013-04; B01 Bogura 2013 annual; B01 Maijdi Court 2014-02; B01 Maijdi Court 2014 annual; B01 Sandwip 2012-12; B01 Sandwip 2012 annual |
| Missing-data sentinel (***) | 29547 | B02 Teknaf 2024-06; B02 Teknaf 2024-07; B02 Teknaf 2024-08; B02 Teknaf 2024-09; B02 Teknaf 2024-10; B02 Teknaf 2024-11 |
| Numeric value stored as text | 14688 | 25.4 -> B37 Dhaka 1995-01 max; 11.3 -> B37 Dhaka 1995-01 min; 28.0 -> B37 Dhaka 1995-02 max; 15.7 -> B37 Dhaka 1995-02 min; 33.8 -> B37 Dhaka 1995-03 max; 19.3 -> B37 Dhaka 1995-03 min |
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
| Sunshine value outside the plausible range 0 to 14, because the longest day at this latitude is close to 13 hours and 30 minutes, so a day cannot hold more than 14 hours of bright sunshine | 33 | B14 Dhaka / 2024 / 11 / 18 = 14.6; B14 Chuadanga / 2024 / 7 / 18 = 20.2; B14 Chuadanga / 2024 / 10 / 7 = 17.9; B14 Chuadanga / 2024 / 10 / 14 = 17; B14 Patuakhali / 2024 / 9 / 30 = 17.3; B14 Ambagan (Ctg) / 2023 / 1 / 13 |
| Row quarantined: Sunshine outside the accepted range | 33 | B14 Dhaka / 2024 / 11 / 18 = 14.6; B14 Chuadanga / 2024 / 7 / 18 = 20.2; B14 Chuadanga / 2024 / 10 / 7 = 17.9; B14 Chuadanga / 2024 / 10 / 14 = 17.0; B14 Patuakhali / 2024 / 9 / 30 = 17.3; B14 Ambagan (Ctg) / 2023 / 1 /  |
| Missing-data sentinel (-) | 24 | B29 Joramtol Shipyard Area 2019 Biochemical Oxygen Demand; B29 Joramtol Shipyard Area 2020 Biochemical Oxygen Demand; B29 Joramtol Shipyard Area 2021 Biochemical Oxygen Demand; B29 Joramtol Shipyard Area 2022 Biochemical |
| Thousands separator written as a decimal point | 22 | 65.173.21 -> 65173.21 (B22 Gazipur 2019-20 Total_Forest_Land); 65.173.21 -> 65173.21 (B22 Gazipur 2020-21 Total_Forest_Land); 65.173.21 -> 65173.21 (B22 Gazipur 2021-22 Total_Forest_Land); 65.173.21 -> 65173.21 (B22 Gazi |
| Month name misspelled in source ('Feburary') | 14 | feburary |
| Unparseable measurement cell | 11 | 'Data is not availaable/ Did not generate By BMD' -> B15 Bogura 2019-11-05 h07; 'Data is not availaable/ Did not generate By BMD' -> B15 Bogura 2019-12-04 h06; 'Instrument Out of Date' -> B18 Satkhira 2021-09-07 h05; 'In |
| Wind Direction value outside the plausible range 0 to 360, because a compass bearing lies in 0 to 360 | 11 | B11 Mymensingh 2022-11-Minimum direction = 9990; B11 Mymensingh 2022-12-Minimum direction = 9990; B11 Mymensingh 2023-2-Minimum direction = 9990; B11 Sitakunda 2020-12-Minimum direction = 9990; B11 Sitakunda 2021-10-Mini |
| Row quarantined: Wind Direction outside the accepted range | 11 | B11 Mymensingh / 2022 / 11 / Minimum = speed=None; direction=9990.0; B11 Mymensingh / 2022 / 12 / Minimum = speed=None; direction=9990.0; B11 Mymensingh / 2023 / 2 / Minimum = speed=None; direction=9990.0; B11 Sitakunda  |
| Sentinel 999 = No Data | 9 | B11 Mymensingh 2022-11 spd; B11 Mymensingh 2022-12 spd; B11 Mymensingh 2023-02 spd; B11 Sitakunda 2020-12 spd; B11 Sitakunda 2021-10 spd; B11 Sitakunda 2021-11 spd |
| Water quality station listed under more than one river | 9 | Pagla -> ['Buriganga River', 'Dlolaikhal']; Karnafully Mohona -> ['Chaktai Khal', 'Karnaphuli River']; 1km Straight from patenga sea beach -> ['Chaktai Khal', 'Karnaphuli River']; Patenga charpara -> ['Chaktai Khal', 'Ka |
| Category label glued to its numeric value | 8 | 0. 00 -> B22 Thakurgaon 2021-22 Acquired_Vested_Forest; Plastic 4193 -> B34 Karnaphuli Mohona 2019 Plastic and Marine Debris; Foamed Plastic 860 -> B34 1 km straight from Patenga Sea Beach 2019 Plastic and Marine Debris; |
| Header or note text found in a station column | 7 | Note: **** Means Missing Data.; Note: *** Means Missing Data/ Data Not Available; Source : Bangladesh Meteorological Department (BMD); Daily Total Sun Shine Hours by Station, 2019-2024; Stations |
| Missing-data sentinel (N/A) | 7 | B15 Bogura 2021-01-06 h06; B15 Bogura 2021-02-07 h07; B15 Bogura 2021-03-08 h04; B17 Dhaka 2021-11-06 h04; B17 Dhaka 2021-12-09 h05; B18 Satkhira 2021-01-12 h04 |
| Missing-data sentinel (*) | 6 | B58 Gazipur 2004-02-30; B58 Gazipur 2004-02-31; B59 Gazipur 2001-03-05; B59 Gazipur 2001-04-28; B59 Gazipur 2005-02-19; B59 Gazipur 2005-08-09 |
| Row quarantined: header or note text parsed as a station | 5 | B23 Table Majhira Demra Ghat / 2022 / Biochemical Oxygen Demand = 10.24; B25 Table Majhira Demra Ghat / 2022 / Chemical Oxygen Demand = 44.42; B26 Table Majhira Demra Ghat / 2022 / pH = 7.32; B28 Table 1.59a: Freshwater  |
| Doubled decimal point repaired | 3 | 27..4 -> B58 Bogura 2021-06-25; 26..2 -> B58 Jessore 2023-09-20; 2..4 -> B59 Gazipur 2022-05-01 |
| Missing-data sentinel (///) | 3 | B58 Tangail 2021-01-01; B58 Tangail 2021-01-02; B58 Tangail 2021-01-03 |
| BMD Sunshine.xls carries Station ID 0.0 on every row and no station name, so its rows cannot be attached to a Station | 2 | Climate : 12 data rows unattachable; Climate Leap year February: 1 data rows unattachable |
| Temperature value outside the plausible range -5 to 50, because the national record runs from about 2 to 45 degrees Celsius | 2 | B57 Khulna / 2023 / 4 / Maximum = 347; B57 Khulna / 2023 / 5 / Maximum = 334 |
| Row quarantined: Temperature outside the accepted range | 2 | B57 Khulna / 2023 / 4 / Maximum = 347.0; B57 Khulna / 2023 / 5 / Maximum = 334.0 |
| Humidity value outside the plausible range 0 to 100, because relative humidity is a percentage and cannot exceed 100 | 2 | B60 Gazipur / 2007 / 5 = 189.6; B60 Patuakhali / 2021 / 6 = 104.35 |
| Row quarantined: Humidity outside the accepted range | 2 | B60 Gazipur / 2007 / 5 = 189.6; B60 Patuakhali / 2021 / 6 = 104.35 |
| Radiation hour range present in source is only 0..13, not the 0..23 the schema anticipates | 1 | hours observed: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] |
| Column number legend row found in a district column | 1 | 2.0 |
| Aggregate "Total" row inside the establishment block | 1 | T3.14 row 6 |
| Source sheet T3.22 publishes only one category row, so Industry_Type is loaded with a single industry and Industry_Usage with one row per fiscal year | 1 | 1 row(s) present |
| T3.22 labels reused waste water as a percentage although its values are outside the percentage range and the table title states thousand litres | 1 | The exact produced and reused volumes remain in pre-BCNF files; the final Percentage is 100 times reused divided by produced |
| BRRI daily readings aggregated to month grain to match the approved schema | 1 | 90737 station-months formed |
| Rainfall value outside the plausible range 0 to 3000, because the wettest recorded month in Bangladesh is below 3000 millimetres | 1 | B59 Sandwip / 2001 / 6 = 3001 |
| Row quarantined: Rainfall outside the accepted range | 1 | B59 Sandwip / 2001 / 6 = 3001.0 |
| Row quarantined: Chemical Oxygen Demand cannot be negative | 1 | B25 Launch Ghat (M) / 2022 / Chemical Oxygen Demand = -44.0 |
| Row quarantined: pH outside 0-14 | 1 | B26 Teesta Bridge (Dn) / 2021 / pH = 14.4 |
| Marine monitoring point stands in the sea, so the source names no river. The water body is recorded as Bay of Bengal so the reading keeps a valid parent row | 1 | 7 stations: 1 km straight from CEPZ, 1 km straight from Patenga Sea Beach, Joramtol Shipyard Area, Karnaphuli Mohona |
| Both waste relations are keyed by fiscal year in the approved diagram, so every published year loads rather than only the latest | 1 | Type_Of_Establishments 12 rows over 3 fiscal years; Industry_Usage 3 rows over 3 |
| Every water quality station name is unique in River_Station, so WQ_Station_Name is the relation primary key and the single column foreign key from Water_Quality is valid | 1 | 321 stations verified |

Total problem occurrences recorded: **132743** across **50** distinct classes.

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

Meteorological precedence used: Bangladesh Meteorological Department, then Bangladesh Rice Research Institute, then Bangladesh Bureau of Statistics. Within one organisation, the block with the newest stated coverage wins; a remaining tie uses the later source occurrence.

### 6.1 Summary, and why the two kinds of conflict are separated

Most conflicts are the two organisations rounding the same reading to a different number of decimal places. A conflict is classed as rounding when the two figures agree to within the tolerance stated for the relation, and as substantive otherwise. Only the substantive conflicts mean the two organisations disagree about what was measured.

| Relation | Tolerance treated as rounding | Precedence applied | Rounding | Substantive | Total |
|---|---|---|---|---|---|
| Humidity_Record | 0.5 | BRRI B60 over BBS B08 | 791 | 878 | 1669 |
| Humidity_Record | 0.5 | BRRI B60 over BBS B09 | 800 | 1210 | 2010 |
| Humidity_Record | 0.5 | BRRI B60 over BBS B10 | 435 | 1167 | 1602 |
| Rainfall_Record | 0.5 | BRRI B59 over BBS B05 | 0 | 1 | 1 |
| Rainfall_Record | 0.5 | BRRI B59 over BBS B07 | 0 | 487 | 487 |
| Sunshine_Record | 0.1 | BRRI B61 over BBS B14 | 136 | 7159 | 7295 |
| Sunshine_Record | 0.1 | BRRI B61 over BRRI B61 | 97 | 3571 | 3668 |
| Temperature_Record | 0.1 | BMD B37 over BRRI B57 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B37 over BRRI B58 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B38 over BRRI B57 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B38 over BRRI B58 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B39 over BRRI B57 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B39 over BRRI B58 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B40 over BRRI B57 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B40 over BRRI B58 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B41 over BRRI B57 | 0 | 391 | 391 |
| Temperature_Record | 0.1 | BMD B41 over BRRI B58 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B42 over BRRI B57 | 0 | 404 | 404 |
| Temperature_Record | 0.1 | BMD B42 over BRRI B58 | 0 | 404 | 404 |
| Temperature_Record | 0.1 | BMD B43 over BRRI B57 | 0 | 406 | 406 |
| Temperature_Record | 0.1 | BMD B43 over BRRI B58 | 0 | 407 | 407 |
| Temperature_Record | 0.1 | BMD B44 over BRRI B57 | 0 | 389 | 389 |
| Temperature_Record | 0.1 | BMD B44 over BRRI B58 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B45 over BRRI B57 | 0 | 384 | 384 |
| Temperature_Record | 0.1 | BMD B45 over BRRI B58 | 0 | 384 | 384 |
| Temperature_Record | 0.1 | BMD B46 over BRRI B57 | 0 | 388 | 388 |
| Temperature_Record | 0.1 | BMD B46 over BRRI B58 | 0 | 388 | 388 |
| Temperature_Record | 0.1 | BMD B47 over BRRI B57 | 0 | 394 | 394 |
| Temperature_Record | 0.1 | BMD B47 over BRRI B58 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B48 over BRRI B57 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B48 over BRRI B58 | 0 | 396 | 396 |
| Temperature_Record | 0.1 | BMD B49 over BRRI B57 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B49 over BRRI B58 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B50 over BRRI B57 | 0 | 408 | 408 |
| Temperature_Record | 0.1 | BMD B50 over BRRI B58 | 0 | 408 | 408 |
| Temperature_Record | 0.1 | BMD B51 over BRRI B57 | 0 | 408 | 408 |
| Temperature_Record | 0.1 | BMD B51 over BRRI B58 | 0 | 403 | 403 |
| Temperature_Record | 0.1 | BMD B52 over BRRI B57 | 0 | 408 | 408 |
| Temperature_Record | 0.1 | BMD B52 over BRRI B58 | 0 | 408 | 408 |
| Temperature_Record | 0.1 | BMD B53 over BBS B01 | 98 | 88 | 186 |
| Temperature_Record | 0.1 | BMD B53 over BBS B03 | 52 | 137 | 189 |
| Temperature_Record | 0.1 | BMD B53 over BRRI B57 | 0 | 201 | 201 |
| Temperature_Record | 0.1 | BMD B53 over BRRI B58 | 0 | 198 | 198 |
| Temperature_Record | 0.1 | BMD B54 over BBS B01 | 20 | 356 | 376 |
| Temperature_Record | 0.1 | BMD B54 over BBS B03 | 8 | 375 | 383 |
| Temperature_Record | 0.1 | BMD B54 over BRRI B57 | 0 | 395 | 395 |
| Temperature_Record | 0.1 | BMD B54 over BRRI B58 | 0 | 388 | 388 |
| Temperature_Record | 0.1 | BRRI B57 over BBS B03 | 0 | 1871 | 1871 |
| Temperature_Record | 0.1 | BRRI B57 over BBS B04 | 0 | 2057 | 2057 |
| Temperature_Record | 0.1 | BRRI B58 over BBS B01 | 0 | 1879 | 1879 |
| Temperature_Record | 0.1 | BRRI B58 over BBS B02 | 0 | 2012 | 2012 |
| Water_Quality | 0.05 | BBS B23 over BBS B23 | 3 | 1 | 4 |
| Water_Quality | 0.05 | BBS B26 over BBS B26 | 3 | 0 | 3 |
| Water_Quality | 0.05 | BBS B27 over BBS B27 | 1 | 0 | 1 |
| Water_Quality | 0.05 | BBS B28 over BBS B28 | 2 | 0 | 2 |
| **Total** | | | **2446** | **37145** | **39591** |

### 6.2 Substantive conflicts

There are **37145** substantive conflicts. The largest are listed below.

| Relation | Key | Source kept | Value kept | Source rejected | Value rejected | Difference |
|---|---|---|---|---|---|---|
| Rainfall_Record | Teknaf | 2020 | 8 | BRRI B59 | 0.0 | BBS B07 | 1177.0 | 1177.00 |
| Rainfall_Record | Teknaf | 2023 | 8 | BRRI B59 | 1164.0 | BBS B07 | 0.0 | 1164.00 |
| Rainfall_Record | Teknaf | 2020 | 7 | BRRI B59 | 0.0 | BBS B07 | 911.0 | 911.00 |
| Rainfall_Record | Teknaf | 2020 | 6 | BRRI B59 | 0.0 | BBS B07 | 636.0 | 636.00 |
| Rainfall_Record | Teknaf | 2020 | 9 | BRRI B59 | 0.0 | BBS B07 | 570.0 | 570.00 |
| Rainfall_Record | Teknaf | 2023 | 10 | BRRI B59 | 283.0 | BBS B07 | 0.0 | 283.00 |
| Rainfall_Record | Madaripur | 2020 | 7 | BRRI B59 | 0.0 | BBS B07 | 273.0 | 273.00 |
| Rainfall_Record | Comilla | 2021 | 7 | BRRI B59 | 365.0 | BBS B07 | 636.0 | 271.00 |
| Rainfall_Record | Sitakunda | 2023 | 8 | BRRI B59 | 991.0 | BBS B07 | 1249.0 | 258.00 |
| Rainfall_Record | Madaripur | 2020 | 6 | BRRI B59 | 0.0 | BBS B07 | 250.0 | 250.00 |
| Rainfall_Record | Madaripur | 2020 | 8 | BRRI B59 | 0.0 | BBS B07 | 247.0 | 247.00 |
| Rainfall_Record | Teknaf | 2023 | 9 | BRRI B59 | 239.0 | BBS B07 | 0.0 | 239.00 |
| Rainfall_Record | Hatiya | 2021 | 6 | BRRI B59 | 1174.0 | BBS B07 | 953.0 | 221.00 |
| Rainfall_Record | Teknaf | 2020 | 10 | BRRI B59 | 0.0 | BBS B07 | 195.0 | 195.00 |
| Rainfall_Record | Madaripur | 2020 | 9 | BRRI B59 | 0.0 | BBS B07 | 194.0 | 194.00 |
| Rainfall_Record | Comilla | 2021 | 6 | BRRI B59 | 439.0 | BBS B07 | 258.0 | 181.00 |
| Rainfall_Record | Sandwip | 2021 | 8 | BRRI B59 | 713.0 | BBS B07 | 894.0 | 181.00 |
| Rainfall_Record | Madaripur | 2020 | 10 | BRRI B59 | 0.0 | BBS B07 | 133.0 | 133.00 |
| Rainfall_Record | Sitakunda | 2021 | 7 | BRRI B59 | 587.0 | BBS B07 | 716.0 | 129.00 |
| Rainfall_Record | Cox's Bazar | 2023 | 10 | BRRI B59 | 209.0 | BBS B07 | 317.0 | 108.00 |
| Rainfall_Record | Sylhet | 2023 | 7 | BRRI B59 | 962.0 | BBS B07 | 1062.0 | 100.00 |
| Rainfall_Record | Teknaf | 2020 | 11 | BRRI B59 | 0.0 | BBS B07 | 98.0 | 98.00 |
| Rainfall_Record | Jessore | 2021 | 4 | BRRI B59 | 4.0 | BBS B07 | 99.0 | 95.00 |
| Rainfall_Record | Kutubdia | 2021 | 9 | BRRI B59 | 133.0 | BBS B07 | 228.0 | 95.00 |
| Rainfall_Record | Sandwip | 2023 | 10 | BRRI B59 | 167.0 | BBS B07 | 259.0 | 92.00 |
| Rainfall_Record | Dhaka | 2023 | 6 | BRRI B59 | 454.0 | BBS B07 | 363.0 | 91.00 |
| Rainfall_Record | Hatiya | 2023 | 8 | BRRI B59 | 757.0 | BBS B07 | 846.0 | 89.00 |
| Rainfall_Record | Feni | 2021 | 6 | BRRI B59 | 618.0 | BBS B07 | 530.0 | 88.00 |
| Rainfall_Record | Faridpur | 2023 | 4 | BRRI B59 | 32.0 | BBS B07 | 118.0 | 86.00 |
| Rainfall_Record | Kutubdia | 2021 | 6 | BRRI B59 | 902.0 | BBS B07 | 816.0 | 86.00 |
| Rainfall_Record | Sitakunda | 2023 | 6 | BRRI B59 | 387.0 | BBS B07 | 473.0 | 86.00 |
| Rainfall_Record | Sylhet | 2023 | 10 | BRRI B59 | 776.0 | BBS B07 | 691.0 | 85.00 |
| Rainfall_Record | Dhaka | 2023 | 7 | BRRI B59 | 160.0 | BBS B07 | 244.0 | 84.00 |
| Rainfall_Record | Sylhet | 2023 | 6 | BRRI B59 | 1351.0 | BBS B07 | 1267.0 | 84.00 |
| Rainfall_Record | Maijdi Court | 2021 | 7 | BRRI B59 | 468.0 | BBS B07 | 551.0 | 83.00 |
| Rainfall_Record | Teknaf | 2023 | 11 | BRRI B59 | 83.0 | BBS B07 | 0.0 | 83.00 |
| Rainfall_Record | Kutubdia | 2021 | 8 | BRRI B59 | 973.0 | BBS B07 | 893.0 | 80.00 |
| Rainfall_Record | Patuakhali | 2021 | 8 | BRRI B59 | 367.0 | BBS B07 | 447.0 | 80.00 |
| Rainfall_Record | Maijdi Court | 2021 | 6 | BRRI B59 | 717.0 | BBS B07 | 639.0 | 78.00 |
| Rainfall_Record | Madaripur | 2023 | 3 | BRRI B59 | 195.0 | BBS B07 | 117.0 | 78.00 |
| Rainfall_Record | Patuakhali | 2021 | 6 | BRRI B59 | 619.0 | BBS B07 | 541.0 | 78.00 |
| Rainfall_Record | Cox's Bazar | 2021 | 6 | BRRI B59 | 808.0 | BBS B07 | 731.0 | 77.00 |
| Rainfall_Record | Madaripur | 2023 | 4 | BRRI B59 | 45.0 | BBS B07 | 122.0 | 77.00 |
| Rainfall_Record | Madaripur | 2021 | 7 | BRRI B59 | 282.0 | BBS B07 | 357.0 | 75.00 |
| Rainfall_Record | Mymensingh | 2023 | 7 | BRRI B59 | 274.0 | BBS B07 | 348.0 | 74.00 |
| Rainfall_Record | Comilla | 2023 | 6 | BRRI B59 | 586.0 | BBS B07 | 514.0 | 72.00 |
| Rainfall_Record | Mymensingh | 2023 | 6 | BRRI B59 | 333.0 | BBS B07 | 261.0 | 72.00 |
| Rainfall_Record | Dinajpur | 2023 | 7 | BRRI B59 | 285.0 | BBS B07 | 356.0 | 71.00 |
| Rainfall_Record | Feni | 2021 | 7 | BRRI B59 | 721.0 | BBS B07 | 792.0 | 71.00 |
| Rainfall_Record | Rangamati | 2021 | 7 | BRRI B59 | 407.0 | BBS B07 | 478.0 | 71.00 |
| Rainfall_Record | Hatiya | 2021 | 7 | BRRI B59 | 725.0 | BBS B07 | 795.0 | 70.00 |
| Rainfall_Record | Mymensingh | 2021 | 8 | BRRI B59 | 435.0 | BBS B07 | 504.0 | 69.00 |
| Rainfall_Record | Jessore | 2023 | 6 | BRRI B59 | 230.0 | BBS B07 | 162.0 | 68.00 |
| Rainfall_Record | Maijdi Court | 2023 | 8 | BRRI B59 | 525.0 | BBS B07 | 593.0 | 68.00 |
| Rainfall_Record | Sandwip | 2021 | 7 | BRRI B59 | 798.0 | BBS B07 | 866.0 | 68.00 |
| Rainfall_Record | Satkhira | 2023 | 8 | BRRI B59 | 359.0 | BBS B07 | 427.0 | 68.00 |
| Rainfall_Record | Bhola | 2023 | 6 | BRRI B59 | 366.0 | BBS B07 | 299.0 | 67.00 |
| Rainfall_Record | Patuakhali | 2021 | 9 | BRRI B59 | 363.0 | BBS B07 | 296.0 | 67.00 |
| Rainfall_Record | Sitakunda | 2021 | 10 | BRRI B59 | 129.0 | BBS B07 | 196.0 | 67.00 |
| Rainfall_Record | Chandpur | 2023 | 8 | BRRI B59 | 530.0 | BBS B07 | 596.0 | 66.00 |
| Rainfall_Record | Hatiya | 2021 | 10 | BRRI B59 | 104.0 | BBS B07 | 169.0 | 65.00 |
| Rainfall_Record | Teknaf | 2021 | 7 | BRRI B59 | 1003.0 | BBS B07 | 1068.0 | 65.00 |
| Rainfall_Record | Barisal | 2021 | 6 | BRRI B59 | 340.0 | BBS B07 | 404.0 | 64.00 |
| Rainfall_Record | Maijdi Court | 2023 | 7 | BRRI B59 | 241.0 | BBS B07 | 177.0 | 64.00 |
| Rainfall_Record | Rangamati | 2021 | 6 | BRRI B59 | 438.0 | BBS B07 | 375.0 | 63.00 |
| Rainfall_Record | Srimangal | 2021 | 7 | BRRI B59 | 233.0 | BBS B07 | 295.0 | 62.00 |
| Rainfall_Record | Teknaf | 2021 | 8 | BRRI B59 | 641.0 | BBS B07 | 703.0 | 62.00 |
| Rainfall_Record | Kutubdia | 2021 | 7 | BRRI B59 | 1084.0 | BBS B07 | 1145.0 | 61.00 |
| Rainfall_Record | Dinajpur | 2023 | 6 | BRRI B59 | 259.0 | BBS B07 | 199.0 | 60.00 |
| Rainfall_Record | Ambagan (Ctg) | 2023 | 8 | BRRI B59 | 1061.0 | BBS B07 | 1120.0 | 59.00 |
| Rainfall_Record | Cox's Bazar | 2021 | 8 | BRRI B59 | 936.0 | BBS B07 | 995.0 | 59.00 |
| Rainfall_Record | Feni | 2021 | 8 | BRRI B59 | 382.0 | BBS B07 | 439.0 | 57.00 |
| Rainfall_Record | Feni | 2023 | 10 | BRRI B59 | 116.0 | BBS B07 | 173.0 | 57.00 |
| Rainfall_Record | Chandpur | 2023 | 6 | BRRI B59 | 223.0 | BBS B07 | 167.0 | 56.00 |
| Rainfall_Record | Srimangal | 2021 | 6 | BRRI B59 | 228.0 | BBS B07 | 172.0 | 56.00 |
| Rainfall_Record | Teknaf | 2023 | 6 | BRRI B59 | 325.0 | BBS B07 | 381.0 | 56.00 |
| Rainfall_Record | Mongla | 2023 | 10 | BRRI B59 | 210.0 | BBS B07 | 265.0 | 55.00 |
| Rainfall_Record | Satkhira | 2023 | 7 | BRRI B59 | 228.0 | BBS B07 | 173.0 | 55.00 |
| Rainfall_Record | Comilla | 2023 | 7 | BRRI B59 | 172.0 | BBS B07 | 226.0 | 54.00 |
| Rainfall_Record | Feni | 2023 | 6 | BRRI B59 | 488.0 | BBS B07 | 434.0 | 54.00 |

The complete list of all **39591** conflicts, rounding and substantive together, is in `csv/BCNF/_Key_Conflicts.csv`.

## 7. Identical duplicates removed

These are rows where two sources publish the same value for the same key. Nothing is lost when the duplicate is dropped.

| Relation | Identical duplicate rows dropped |
|---|---|
| Sunshine_Record | 41027 |
| Rainfall_Record | 4854 |
| Temperature_Record | 452 |
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
| Every foreign key value exists in the parent relation | 28 | 0 |

The primary-key and foreign-key checks found no violation. Other domain and cross-row checks are listed separately in `DATA_REVIEW.md`.
