"""Shared helpers for the 0NF -> BCNF normalization run.

Read-only against every source file. All output stays under normalization/.
No pandas: openpyxl / xlrd / csv only.
"""
import csv
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
NORMALIZATION_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(NORMALIZATION_DIR)
SRC = os.path.abspath(os.environ.get(
    'DBMS_SOURCE_DIR', os.path.join(ROOT, 'Selected_Source_Files'))) + os.sep
OUT = os.path.abspath(os.environ.get(
    'DBMS_NORMALIZATION_DIR', NORMALIZATION_DIR)) + os.sep
CSVDIR = os.path.join(OUT, 'csv') + os.sep

BBS_XLSX = SRC + 'Govt/BBS/BBS_Time_Series_Environmental_Database.xlsx'
BMD_TEMP = SRC + 'Formatted_Data/BMD/Temperature Data/Temperature Data.xlsx'
BMD_SUN = SRC + 'Govt/BMD/Sunshine.xls'
BRRI_DIR = SRC + 'Govt/BRRI/'
BWDB_RIVERS = SRC + 'Govt/BWDB/BWDB_Rivers_Information.csv'
BWDB_GW = (SRC + 'Formatted_Data/BWDB/BWDB_Groundwater_Weekly_Data_2018/'
           'BWDB_Groundwater_Weekly_Data_2018.xlsx')

ZERO_NF_ROW_CAP = 200

ANOM = {}
ANOM_SAMPLE = {}


def anom(cls, detail=''):
    ANOM[cls] = ANOM.get(cls, 0) + 1
    if detail:
        s = ANOM_SAMPLE.setdefault(cls, [])
        if len(s) < 6 and detail not in s:
            s.append(detail)


MISSING_TOKENS = {'*', '**', '***', '****', '*****', '-', '--', 'na', 'n/a',
                  'nd', 'n.d.', 'blank', '', '#div/0!', '///', '//', '#n/a',
                  '#value!', '#ref!', '.', '..'}
TRACE_TOKENS = {'t', 'tr', 'trace'}
NIL_TOKENS = {'nil', 'nill', 'niil'}


def clean_text(v):
    """Whitespace / unicode normalised text form of a cell."""
    if v is None:
        return ''
    s = str(v)
    s = unicodedata.normalize('NFKC', s)
    s = s.replace('‘', "'").replace('’', "'").replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def num(v, ctx='', allow_trace=False):
    """Parse a measurement cell.

    Returns (value_or_None, kind) where kind is one of
    'num', 'empty', 'missing', 'trace', 'nil', 'nodata', 'unparsed'.
    Missing values are returned as None so the caller writes an empty cell.
    """
    if v is None:
        return None, 'empty'
    if isinstance(v, bool):
        return None, 'unparsed'
    if isinstance(v, (int, float)):
        f = float(v)
        if f == 999.0:
            anom('Sentinel 999 = No Data', ctx)
            return None, 'nodata'
        return f, 'num'
    s = clean_text(v)
    if s == '':
        return None, 'empty'
    low = s.lower()
    if low in MISSING_TOKENS:
        anom('Missing-data sentinel (%s)' % s, ctx)
        return None, 'missing'
    if low in NIL_TOKENS:
        anom('Textual nil / Nill in place of zero', '%s -> %s' % (s, ctx))
        return 0.0, 'nil'
    if low in TRACE_TOKENS:
        if allow_trace:
            anom("Rainfall trace sentinel 'T' substituted with 0", ctx)
            return 0.0, 'trace'
        anom("Trace sentinel 'T' outside rainfall", ctx)
        return None, 'unparsed'
    if set(low) <= {'*', ' '}:
        anom('Missing-data sentinel (asterisks)', ctx)
        return None, 'missing'
    m = re.match(r'^(-?\d+(?:\.\d+)?)\s+[\*\d]+$', s)
    if m:
        anom('Value with trailing footnote marker', '%s -> %s' % (s, ctx))
        return float(m.group(1)), 'num'
    m = re.match(r'^(-?\d+)\.\.(\d+)$', s)
    if m:
        anom('Doubled decimal point repaired', '%s -> %s' % (s, ctx))
        return float('%s.%s' % (m.group(1), m.group(2))), 'num'
    m = re.match(r'^(\d+)\.(\d{3})\.(\d+)$', s)
    if m:
        fixed = float('%s%s.%s' % (m.group(1), m.group(2), m.group(3)))
        anom('Thousands separator written as a decimal point',
             '%s -> %.2f (%s)' % (s, fixed, ctx))
        return fixed, 'num'
    s2 = s.replace(',', '')
    try:
        f = float(s2)
        if f == 999.0:
            anom('Sentinel 999 = No Data', ctx)
            return None, 'nodata'
        anom('Numeric value stored as text', '%s -> %s' % (s, ctx))
        return f, 'num'
    except ValueError:
        pass
    m = re.match(r'^(.*?)(\d+(?:\.\d+)?)$', s)
    if m and m.group(1).strip():
        anom('Category label glued to its numeric value',
             '%s -> %s' % (s, ctx))
        return float(m.group(2)), 'num'
    anom('Unparseable measurement cell', '%r -> %s' % (s, ctx))
    return None, 'unparsed'


def as_int(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = clean_text(v)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


MONTHS = {
    'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'feburary': 2,
    'mar': 3, 'march': 3, 'apr': 4, 'april': 4, 'may': 5,
    'jun': 6, 'june': 6, 'jul': 7, 'july': 7, 'aug': 8, 'august': 8,
    'sep': 9, 'sept': 9, 'spt': 9, 'september': 9,
    'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
    'dec': 12, 'december': 12,
}


def month_no(v):
    """Month name or number -> 1..12, else None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        n = int(v)
        return n if 1 <= n <= 12 else None
    s = clean_text(v).lower().rstrip('.')
    if not s:
        return None
    if s in MONTHS:
        if s == 'feburary':
            anom("Month name misspelled in source ('Feburary')", s)
        return MONTHS[s]
    try:
        n = int(float(s))
        return n if 1 <= n <= 12 else None
    except ValueError:
        return None


DAYS_IN_MONTH = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
                 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


STATION_JUNK = {
    'station', 'stations', 'name of station', 'station/year', 'station name',
    'station  name', 'note : *** means missing data', 'country', 'year',
    'district', 'district name', 'sl. no', 'total', 'grand total',
    'bangladesh', 'annual', 'month', 'day', 'days',
}

STATION_CANON = {
    'hatia': 'Hatiya', 'hatiya': 'Hatiya',
    'khapupara': 'Khepupara', 'khepupara': 'Khepupara',
    'srimongal': 'Srimangal', 'srimangal': 'Srimangal',
    'sydpur': 'Sayedpur', 'syedpur': 'Sayedpur', 'sayedpur': 'Sayedpur',
    'jashore': 'Jessore', 'jessore': 'Jessore',
    'm.court': 'Maijdi Court', 'm_court': 'Maijdi Court',
    'm.court.': 'Maijdi Court', 'maijdi court': 'Maijdi Court',
    'maijdicourt': 'Maijdi Court',
    "cox's bazar": "Cox's Bazar", "cox'sbazar": "Cox's Bazar",
    "cox`s bazar": "Cox's Bazar", "cox's_bazar": "Cox's Bazar",
    "cox's": "Cox's Bazar", "cox`sbazar": "Cox's Bazar",
    'ambagan': 'Ambagan (Ctg)', 'ambagan(ctg)': 'Ambagan (Ctg)',
    'ambagan(ctg': 'Ambagan (Ctg)', 'ctg. (ambagan)': 'Ambagan (Ctg)',
    'ctg(ambagan)': 'Ambagan (Ctg)', 'chi(ambagan)': 'Ambagan (Ctg)',
    'ambagan_ctg': 'Ambagan (Ctg)', 'ambagan (ctg)': 'Ambagan (Ctg)',
    'ctg. (patanga)': 'Chittagong (Patenga)',
    'ctg(patenga)': 'Chittagong (Patenga)',
    'chi(patanga)': 'Chittagong (Patenga)',
    'ctg. (patenga)': 'Chittagong (Patenga)',
    'bogra': 'Bogura', 'bogura': 'Bogura',
    'ishardi': 'Ishurdi', 'ishurdi': 'Ishurdi',
    'chittagong': 'Chittagong', 'chattogram': 'Chittagong',
    'comilla': 'Comilla', 'cumilla': 'Comilla', 'kumilla': 'Comilla',
}

STATION_MAP_LOG = {}
STATION_DROPPED = {}


def canon_station(v):
    """Canonical station name, or None if the value is not a station."""
    s = clean_text(v)
    if not s:
        return None
    low = s.lower().rstrip('.').strip()
    if low in STATION_JUNK or s.lower() in STATION_JUNK:
        STATION_DROPPED[s] = STATION_DROPPED.get(s, 0) + 1
        anom('Header or note text found in a station column', s)
        return None
    if low.startswith(('note', 'source', 'monthly', 'daily', 'radiation',
                       'table ', 'freshwater', 'marine')):
        STATION_DROPPED[s] = STATION_DROPPED.get(s, 0) + 1
        anom('Header or note text found in a station column', s)
        return None
    c = STATION_CANON.get(low)
    if c is None:
        if not any(ch.isupper() for ch in s):
            c = ' '.join(w[:1].upper() + w[1:] for w in s.split(' '))
            anom('Station name published entirely in lower case',
                 '%s -> %s' % (s, c))
        else:
            c = s
    if c != s:
        STATION_MAP_LOG[s] = c
    return c


DISTRICT_CANON = {
    'mymenshingh': 'Mymensingh', 'mymensingh': 'Mymensingh',
    'hobigonj': 'Habiganj', 'habiganj': 'Habiganj',
    'maulavibazar': 'Moulvi Bazar', 'moulvi bazar': 'Moulvi Bazar',
    'sunamgonj': 'Sunamganj', 'sunamganj': 'Sunamganj',
    'chittaganj': 'Chattogram', 'chattogram': 'Chattogram',
    'cumilla': 'Kumilla', 'kumilla': 'Kumilla', 'comilla': 'Kumilla',
    'satkhiar': 'Satkhira', 'satkhira': 'Satkhira',
    'perojpur': 'Pirojpur', 'pirojpur': 'Pirojpur',
    'khagrachari': 'Khagrachhari', 'khagrachhari': 'Khagrachhari',
    'jhalokathi': 'Jhalokathi', 'barisal': 'Barisal',
}
DISTRICT_MAP_LOG = {}


def canon_district(v):
    s = clean_text(v)
    if not s:
        return None
    low = s.lower()
    if low in ('total', 'grand total', 'district', 'district name', 'sl. no'):
        return None
    if re.match(r'^\d+(\.\d+)?$', low):
        anom('Column number legend row found in a district column', s)
        return None
    c = DISTRICT_CANON.get(low, s)
    if c != s:
        DISTRICT_MAP_LOG[s] = c
    return c


RIVER_MAP_LOG = {}


def river_key(s):
    s = clean_text(s)
    s = re.sub(r'\s*rivers?\s*$', '', s, flags=re.I)
    s = re.sub(r'\(.*?\)', '', s)
    return re.sub(r'\s+', ' ', s).strip().lower()


RIVER_ALIAS = {
    'bhrammaputra': 'Old Brahmaputra',
    'dhalaswary': 'Dhaleshwari',
    'gorai': 'Garai',
    'kaligonga': 'Kaliganga (Manikganj)',
    'karnaphuli': 'Karnafuli',
    'khakshiali': 'Kakshiali',
    'kirtonkhola': 'Kirtankhola',
    'korotoa': 'Karatoa',
    'kushiara': 'Kushiyara',
    'mathavanga': 'Mathabhaga',
    'modhumoti': 'Madhumati',
    'shitalakhya': 'Shetalakhya',
    'turagh': 'Turag',
    'bhairab': 'Bhairab (Bagerhat)',
    'jamuna': 'Brahmaputra-Jamuna',
    'meghna': 'Meghna (lower)',
    'rupsha': 'Rupsa (Khulna)',
}


def fmt(v):
    """Format a value for a CSV cell. None -> empty cell (never 0)."""
    if v is None:
        return ''
    if isinstance(v, float):
        if v != v:
            return ''
        if abs(v - round(v)) < 1e-9 and abs(v) < 1e15:
            return str(int(round(v)))
        return ('%.6f' % v).rstrip('0').rstrip('.')
    if isinstance(v, str):
        return clean_text(v)
    return str(v)


def write_csv(stage, name, header, rows, cap=None, note=None):
    d = os.path.join(CSVDIR, stage)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name + '.csv')
    n = len(rows)
    out = rows if cap is None or n <= cap else rows[:cap]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in out:
            w.writerow([fmt(c) for c in r])
    if cap is not None and n > cap:
        with open(path.replace('.csv', '.meta.txt'), 'w',
                  encoding='utf-8') as f:
            f.write('File: %s.csv\n' % name)
            f.write('This CSV is a REPRESENTATIVE EXTRACT, not the full '
                    'block.\n')
            f.write('Rows written to the CSV : %d\n' % len(out))
            f.write('TRUE full row count     : %d\n' % n)
            f.write('Rows omitted            : %d\n' % (n - len(out)))
            f.write('The extract is the first %d data rows in source order, '
                    'after the header rows.\n' % len(out))
            if note:
                f.write('\n%s\n' % note)
    return n, len(out)


def write_raw_csv(name, rows, ncols, note=None):
    """0NF writer: rows are written verbatim, no header row is synthesised."""
    d = os.path.join(CSVDIR, '0NF')
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name + '.csv')
    n = len(rows)
    out = rows if n <= ZERO_NF_ROW_CAP else rows[:ZERO_NF_ROW_CAP]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        for r in out:
            r = list(r) + [None] * (ncols - len(r))
            w.writerow([fmt(c) for c in r[:ncols]])
    if n > ZERO_NF_ROW_CAP:
        with open(path.replace('.csv', '.meta.txt'), 'w',
                  encoding='utf-8') as f:
            f.write('File: %s.csv\n' % name)
            f.write('This 0NF CSV is a REPRESENTATIVE EXTRACT of the raw '
                    'source block.\n')
            f.write('It is NOT the complete block and has been truncated on '
                    'purpose.\n\n')
            f.write('Rows written to the CSV : %d\n' % len(out))
            f.write('TRUE full row count     : %d\n' % n)
            f.write('Rows omitted            : %d\n' % (n - len(out)))
            f.write('Column count            : %d\n' % ncols)
            f.write('\nThe rows written are the first %d rows of the block in '
                    'source order,\nincluding every header row, merged-header '
                    'artefact and repeating\ncolumn group exactly as '
                    'published.\n' % len(out))
            if note:
                f.write('\n%s\n' % note)
    return n, len(out)
