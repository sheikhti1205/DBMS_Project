# Team 8 External Workbook Download / Access Log

This log exists so network and repository actions are visible before retrying or manually completing access to Team 8's external collaboration workbook. Team 8 is a separate team; this is not Team 7's primary resource workbook.

## Security scope for any future retry

- Required domain only: `docs.google.com`
- Intended method only: export the shared Google Sheet as `.xlsx`
- No repository secrets, tokens, cookies, or local credentials should be sent in commands.
- Do not run downloaded files or macros; treat the workbook as data only.

## Shared file

- Google Sheets URL: `https://docs.google.com/spreadsheets/d/1_uTFK75woX6g20A4XR_-lkcWFijNgK5U/edit?usp=sharing&ouid=115021159123362427080&rtpof=true&sd=true`
- File ID: `1_uTFK75woX6g20A4XR_-lkcWFijNgK5U`
- Possible future Team-8 source copy path: `Selected_Source_Files/Data_Sheets/Team-8/Team-8_BD_Environmental_Data_Resources.xlsx`

## Commands attempted previously

```bash
curl -L --fail --retry 3 --retry-delay 2 \
  -o /tmp/Team-8_BD_Environmental_Data_Resources.xlsx.download \
  "https://docs.google.com/spreadsheets/d/1_uTFK75woX6g20A4XR_-lkcWFijNgK5U/export?format=xlsx"
```

Result: failed with HTTP 403.

```bash
curl -L -A 'Mozilla/5.0' -sS \
  -w '%{http_code}' \
  -o /tmp/team8_try.xlsx \
  "https://docs.google.com/spreadsheets/d/1_uTFK75woX6g20A4XR_-lkcWFijNgK5U/export?format=xlsx&id=1_uTFK75woX6g20A4XR_-lkcWFijNgK5U"
```

Result: failed with a tunnel 403 response in this environment.

```bash
curl -L -A 'Mozilla/5.0' -sS \
  -w '%{http_code}' \
  -o /tmp/team8_try.xlsx \
  "https://docs.google.com/spreadsheets/export?id=1_uTFK75woX6g20A4XR_-lkcWFijNgK5U&exportFormat=xlsx"
```

Result: failed with a tunnel 403 response in this environment.

## Corrective action taken

- Removed the prior preview-derived workbook from the repository because it was not a verified full export and could make Team 8's external file look like a Team 7-owned source.
- Kept source metadata and this access log under `Selected_Source_Files/Collaboration_References/Team-8/` so future collaboration or overlap review has clear provenance without mixing Team 8 into Team 7's core resources.

## Future retry checklist

Before retrying network access, log the exact command first and restrict it to `docs.google.com`. After download, verify the file before committing:

```bash
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
p = Path('Selected_Source_Files/Data_Sheets/Team-8/Team-8_BD_Environmental_Data_Resources.xlsx')
print('exists', p.exists())
print('size_bytes', p.stat().st_size if p.exists() else 0)
with ZipFile(p) as z:
    print('zip_test', z.testzip() or 'ok')
    print('members', len(z.namelist()))
PY
```
