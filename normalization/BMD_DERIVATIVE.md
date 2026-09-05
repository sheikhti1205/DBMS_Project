# BMD temperature workbook check

The retained `Govt/BMD/Temperature Data.pdf` is the publication. The project
uses `Formatted_Data/BMD/Temperature Data/Temperature Data.xlsx` as its
structured derivative. The committed pipeline reads this workbook directly;
it does not recreate it from the PDF. The historical conversion procedure
was not recorded, so no particular OCR tool or manual method is asserted.

The workbook has 18 sheets for 1995–2012. A separate read-only check compares
the first, middle and last station row on each sheet with text extracted from
the corresponding PDF page. Each row contains 12 maximum and 12 minimum
monthly values. All 54 sampled rows (1,296 values) match. This is a sample,
not an exhaustive cell comparison, and does not validate the publisher's
measurements themselves. Missing markers are compared as text; numbers are
compared numerically.

Run from the repository root with the project Python environment, openpyxl,
and Poppler's `pdftotext` available:

```bash
python3 -B normalization/scripts/verify_bmd_derivative.py \
  --source-dir "/path/to/Selected_Source_Files" \
  --output normalization/review/bmd_derivative_check.json
```

The [result](review/bmd_derivative_check.json) records each sampled sheet,
year, station and PDF page, together with SHA-256 hashes of both input files.
Re-run the check if either input changes. Source files and database contents
are not modified by the check.