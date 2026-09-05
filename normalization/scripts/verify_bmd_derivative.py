"""Compare representative rows of the retained BMD workbook with PDF text.

Requires openpyxl and Poppler pdftotext. This checks a derivative, not the
historical conversion method. Inputs are read-only; output records hashes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import openpyxl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pdf = args.source_dir / 'Govt/BMD/Temperature Data.pdf'
    xlsx = args.source_dir / 'Formatted_Data/BMD/Temperature Data/Temperature Data.xlsx'
    text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
    pages = text.split('\f')
    workbook = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    checks = []
    for sheet in workbook:
        rows = list(sheet.values)
        year = re.search(r'\b(?:19|20)\d{2}\b', str(rows[0][0])).group()
        candidates = [(i+1,p) for i,p in enumerate(pages) if re.search(r'Monthly Temperature.*'+year,p)]
        data = [r for r in rows[2:] if r[0] and len(r) >= 25]
        for row in [data[0], data[len(data)//2], data[-1]]:
            station = str(row[0]).strip()
            matches = [(number,line) for number,page in candidates for line in page.splitlines()
                       if line.strip().startswith(station+' ')]
            expected = [str(v).strip() if v is not None else '' for v in row[1:25]]
            def same(a,b):
                try: return float(a) == float(b)
                except ValueError: return a == b
            actual = matches[0][1].strip()[len(station):].split() if len(matches)==1 else []
            ok = len(actual)==24 and all(same(a,b) for a,b in zip(actual,expected))
            checks.append({'sheet': sheet.title, 'year': year, 'station': station,
                           'pdf_page': matches[0][0] if matches else None,
                           'measurements':24, 'matched':ok,
                           **({} if ok else {'pdf_values':actual,'xlsx_values':expected})})
    result = {'scope':'First, middle and last station row in every workbook sheet; 24 monthly max/min cells per row. Not an exhaustive audit.',
              'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
              'xlsx_sha256':hashlib.sha256(xlsx.read_bytes()).hexdigest(), 'checks':checks}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('Matched station rows:',sum(c['matched'] for c in checks),'/',len(checks))
    for c in checks:
        if not c['matched']:print(c)
    raise SystemExit(0 if all(c['matched'] for c in checks) else 1)

if __name__ == '__main__':
    main()