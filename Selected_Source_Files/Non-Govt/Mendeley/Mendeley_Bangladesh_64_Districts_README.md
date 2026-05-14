# Bangladesh 64 Districts Daily Climate and Air Quality (AQI) Dataset (2023-2025)

## Overview
This dataset contains a comprehensive, daily time-series record of meteorological and air quality parameters for all 64 administrative districts of Bangladesh. The data spans a three-year period from **January 1, 2023, to December 31, 2025**. It is designed to assist researchers, data scientists, and environmentalists in studying climate patterns, spatial weather distribution, air pollution trends, and machine learning-based forecasting models.

## Dataset Characteristics
* **Spatial Coverage:** 64 Districts of Bangladesh
* **Temporal Coverage:** January 01, 2023 – December 31, 2025
* **Temporal Resolution:** Daily
* **Format:** Comma-Separated Values (.csv)
* **Total Files:** 64 individual CSV files (compressed in a `.zip` archive)

## Data Dictionary (Column Descriptions)
Each district's `.csv` file contains the following variables:

| Column Name | Description | Unit |
| :--- | :--- | :--- |
| `Date` | The date of the recorded observation (Format: YYYY-MM-DD) | - |
| `District` | The name of the administrative district | - |
| `Latitude` | The geographical latitude of the district center | Decimal Degrees |
| `Longitude` | The geographical longitude of the district center | Decimal Degrees |
| `Avg_Temperature_C` | Daily mean temperature | Celsius (°C) |
| `Rainfall_mm` | Total daily precipitation/rainfall sum | Millimeters (mm) |
| `Max_Wind_Speed_kmh` | Maximum wind speed recorded during the day | Kilometers per hour (km/h) |
| `PM10` | Daily average concentration of particulate matter < 10 micrometers | µg/m³ |
| `PM2.5` | Daily average concentration of particulate matter < 2.5 micrometers | µg/m³ |
| `AQI_Level` | Daily average United States Air Quality Index (US AQI) | Index Value |

## Methodology & Data Collection Pipeline
The dataset was systematically generated using automated Python scripting. 
1. **Source:** Data was retrieved via the open-source **Open-Meteo** API (Historical Weather API and Air Quality API).
2. **Extraction:** Python's `requests` and `pandas` libraries were utilized to fetch and parse the JSON responses.
3. **Aggregation:** While meteorological data was directly fetched at a daily resolution, air quality data (PM10, PM2.5, AQI) was fetched at an hourly resolution and aggregated into daily arithmetic means to ensure consistency.
4. **Missing Values:** Minimal to no missing values. In rare cases of API unavailability for specific hours, data was handled via pandas' `.dropna()` or `.mean()` aggregation.

## File Structure
The primary download is a compressed archive (`Bangladesh_64Districts_weather_Data.zip`). Upon extraction, it yields 64 individual CSV files named according to the district (e.g., `Dhaka_Climate_AQI_Data.csv`, `Chittagong_Climate_AQI_Data.csv`).

## Potential Applications
* Spatiotemporal climate change analysis.
* Air quality monitoring and public health research.
* Training Machine Learning (ML) and Deep Learning (DL) models for time-series forecasting.
* Agricultural impact studies correlating rainfall and temperature.

