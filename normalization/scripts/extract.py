"""0NF -> BCNF extraction for the Bangladesh environmental database.

Reads only from Selected_Source_Files. Writes only under normalization/.
Run:  python normalization/scripts/extract.py
"""
import calendar
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blocks as BK
from nlib import (anom, ANOM, ANOM_SAMPLE, canon_district,
                  canon_station, clean_text, month_no, num, as_int,
                  river_key, RIVER_ALIAS, RIVER_MAP_LOG,
                  STATION_DROPPED, STATION_MAP_LOG, DISTRICT_MAP_LOG,
                  write_csv, OUT)

TEMP = []
HUM = []
RAIN = []
WIND = []
EVENT = []
SUN = []
RAD = []
WQ = []
GW = []
FOREST = []
IND = []
EST = []
RIVREG = []

ANNUAL = []
STLOC = []

CELLS_READ = collections.Counter()
CELLS_KEPT = collections.Counter()
MISSING = collections.Counter()

TRACE = []


def T(rel, attr, org, fil, sheet, col, xform):
    TRACE.append((rel, attr, org, fil, sheet, col, xform))


def seen(block, kept, val_kind):
    CELLS_READ[block] += 1
    if kept:
        CELLS_KEPT[block] += 1
    elif val_kind in ('missing', 'nodata', 'unparsed', 'empty'):
        MISSING[block] += 1


def days_in(year, month):
    try:
        return calendar.monthrange(int(year), int(month))[1]
    except Exception:
        return 31


def valid_day(year, month, day, ctx):
    if day is None or month is None or year is None:
        return False
    if not 1 <= day <= days_in(year, month):
        anom('Day number beyond the length of the month',
             '%s-%02d day %s (%s)' % (year, month, day, ctx))
        return False
    return True


MONTH_COLS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def is_station_label(v):
    s = clean_text(v)
    return s.lower().startswith('station :') or s.lower().startswith('station:')


def station_from_label(v):
    s = clean_text(v)
    return canon_station(s.split(':', 1)[1])


def parse_rowform_month(bid, sheet, lo, hi, mcol0, kind, typ):
    """T1.02 / T1.03 block 1: 'Station : X' label rows then year rows,
    months in columns mcol0..mcol0+11."""
    rs = BK.bbs_rows(sheet)[lo:hi]
    st = None
    for r in rs:
        r = list(r) + [None] * 40
        if is_station_label(r[1]):
            st = station_from_label(r[1])
            continue
        y = as_int(r[1])
        if st is None or y is None or not 1900 <= y <= 2100:
            continue
        for k in range(12):
            v, kd = num(r[mcol0 + k], '%s %s %d-%02d' % (bid, st, y, k + 1))
            seen(bid, v is not None, kd)
            if v is None:
                continue
            if kind == 'temp':
                TEMP.append((st, y, k + 1, typ, v, bid))
        v, kd = num(r[mcol0 + 12], '%s %s %d annual' % (bid, st, y))
        if v is not None:
            ANNUAL.append((st, y, 'Annual ' + kind, v, bid))


def parse_rowform_wind(bid, sheet, lo, hi, typ):
    """T1.08 / T1.10: 'Station : X' rows then year rows; each month is a
    (speed, direction) column pair starting at column 2."""
    rs = BK.bbs_rows(sheet)[lo:hi]
    st = None
    for r in rs:
        r = list(r) + [None] * 40
        if is_station_label(r[1]):
            st = station_from_label(r[1])
            for j in range(2, 20):
                s = clean_text(r[j])
                if s.lower().startswith('lat'):
                    lon = ''
                    for j2 in range(j + 1, 20):
                        s2 = clean_text(r[j2])
                        if s2.lower().startswith('long'):
                            lon = s2
                            break
                    if st:
                        STLOC.append((st, s, lon, bid))
                        anom('Station latitude/longitude embedded in a label '
                             'row', '%s %s %s' % (st, s, lon))
                    break
            continue
        y = as_int(r[1])
        if st is None or y is None or not 1900 <= y <= 2100:
            continue
        for k in range(12):
            sc, dc = 2 + 2 * k, 3 + 2 * k
            sp, k1 = num(r[sc], '%s %s %d-%02d spd' % (bid, st, y, k + 1))
            di, k2 = num(r[dc], '%s %s %d-%02d dir' % (bid, st, y, k + 1))
            seen(bid, sp is not None or di is not None, k1)
            if sp is None and di is None:
                continue
            WIND.append((st, y, k + 1, typ, sp, di, bid))


def parse_colform_year(bid, sheet, lo, hi, scol, ycol, mcol0, target,
                       annual_col=None, annual_label=None):
    """One row per (station, year), 12 month columns.
    T1.05, T1.06, T1.19, T1.19a."""
    rs = BK.bbs_rows(sheet)[lo:hi]
    for r in rs:
        r = list(r) + [None] * 40
        st = canon_station(r[scol])
        y = as_int(r[ycol])
        if st is None or y is None or not 1900 <= y <= 2100:
            continue
        for k in range(12):
            v, kd = num(r[mcol0 + k], '%s %s %d-%02d' % (bid, st, y, k + 1),
                        allow_trace=(target == 'rain'))
            seen(bid, v is not None, kd)
            if v is None:
                continue
            if target == 'rain':
                RAIN.append((st, y, k + 1, v, bid))
            elif target == 'hum':
                if not 0 <= v <= 100:
                    anom('Humidity percentage outside 0-100',
                         '%s %s %d-%02d = %s' % (bid, st, y, k + 1, v))
                HUM.append((st, y, k + 1, v, bid))
            elif target == 'thunder':
                EVENT.append((st, y, k + 1, v, None, bid))
            elif target == 'lightning':
                EVENT.append((st, y, k + 1, None, v, bid))
        if annual_col is not None:
            v, kd = num(r[annual_col], '%s %s %d annual' % (bid, st, y),
                        allow_trace=(target == 'rain'))
            if v is not None:
                ANNUAL.append((st, y, annual_label, v, bid))


def parse_wide_year_blocks(bid, sheet, lo, hi, scol, yearheads, typ):
    """T1.02 / T1.03 block 2: one row per station, 8 year blocks of 12
    months. yearheads is [(col, year), ...]."""
    rs = BK.bbs_rows(sheet)[lo:hi]
    for r in rs:
        r = list(r) + [None] * 110
        st = canon_station(r[scol])
        if st is None:
            continue
        for c0, y in yearheads:
            for k in range(12):
                v, kd = num(r[c0 + k],
                            '%s %s %d-%02d' % (bid, st, y, k + 1))
                seen(bid, v is not None, kd)
                if v is not None:
                    TEMP.append((st, y, k + 1, typ, v, bid))


def parse_t113():
    bid = 'B14'
    rs = BK.bbs_rows('T1.13')[0:2525]
    for r in rs:
        r = list(r) + [None] * 40
        st = canon_station(r[1])
        y = as_int(r[2])
        m = month_no(r[3])
        if st is None or y is None or m is None or not 1900 <= y <= 2100:
            continue
        for d in range(1, 32):
            v, kd = num(r[3 + d], '%s %s %d-%02d-%02d' % (bid, st, y, m, d))
            seen(bid, v is not None, kd)
            if v is None:
                continue
            if not valid_day(y, m, d, '%s %s' % (bid, st)):
                continue
            if not 0 <= v <= 24:
                anom('Sunshine hours outside 0-24',
                     '%s %s %d-%02d-%02d = %s' % (bid, st, y, m, d, v))
            SUN.append((st, y, m, d, v, bid))


RAD_BLOCKS = [('B15', 'Bogura', 4, 186), ('B16', 'Dinajpur', 190, 375),
              ('B17', 'Dhaka', 379, 562), ('B18', 'Satkhira', 566, 749),
              ('B19', 'Chuadanga', 753, 936)]
RAD_YEARS = [(2019, 4), (2020, 35), (2021, 66), (2022, 97), (2023, 128),
             (2024, 159)]


def parse_t114():
    rs = BK.bbs_rows('T1.14')
    hours_seen = set()
    for bid, stname, lo, hi in RAD_BLOCKS:
        st = canon_station(stname)
        for i in range(lo, min(hi, len(rs))):
            r = list(rs[i]) + [None] * 215
            m = month_no(r[2])
            hr_raw = clean_text(r[3])
            if m is None:
                continue
            if hr_raw.lower() in ('total', 'sum', 'average', 'mean'):
                anom('Aggregate "Total" row inside the radiation day grid',
                     '%s %s row %d' % (bid, stname, i))
                continue
            hr = as_int(r[3])
            if hr is None:
                continue
            if not 0 <= hr <= 23:
                anom('Radiation hour outside 0-23',
                     '%s %s hour=%s' % (bid, stname, hr))
                continue
            hours_seen.add(hr)
            for y, c0 in RAD_YEARS:
                for d in range(1, 32):
                    v, kd = num(r[c0 + d - 1],
                                '%s %s %d-%02d-%02d h%02d'
                                % (bid, stname, y, m, d, hr))
                    seen(bid, v is not None, kd)
                    if v is None:
                        continue
                    if not valid_day(y, m, d, '%s %s' % (bid, stname)):
                        continue
                    RAD.append((st, y, m, d, hr, v, bid))
    if hours_seen:
        anom('Radiation hour range present in source is only %d..%d, not the '
             '0..23 the schema anticipates'
             % (min(hours_seen), max(hours_seen)),
             'hours observed: %s' % sorted(hours_seen))


FOREST_MEASURES = [
    ('Reserved_Forest_Section_20_Acre', 0),
    ('Reserved_Forest_Section_4_6_Acre', 1),
    ('Protected_Area', 2),
    ('Acquired_Vested_Forest', 3),
    ('Unclassed_State_Forest_FD_Acre', 4),
    ('Total_Forest_FD_Acre', 5),
    ('Unclassed_State_Forest_Admin_Acre', 6),
    ('Total_Forest_Land', 7),
]
FOREST_FY = [(3, '2019-20'), (11, '2020-21'), (19, '2021-22'),
             (27, '2022-23'), (35, '2023-24')]


def parse_t166():
    bid = 'B22'
    rs = BK.bbs_rows('T1.66')[0:42]
    for r in rs:
        r = list(r) + [None] * 46
        d = canon_district(r[2])
        if d is None:
            continue
        if as_int(r[1]) is None:
            continue
        for c0, fy in FOREST_FY:
            y1, y2 = int(fy[:4]), int(fy[:2] + fy[5:])
            vals = {}
            got = False
            for attr, off in FOREST_MEASURES:
                v, kd = num(r[c0 + off], '%s %s %s %s' % (bid, d, fy, attr))
                seen(bid, v is not None, kd)
                vals[attr] = v
                if v is not None:
                    got = True
            if not got:
                continue
            comp = [vals['Reserved_Forest_Section_20_Acre'],
                    vals['Reserved_Forest_Section_4_6_Acre'],
                    vals['Protected_Area'],
                    vals['Acquired_Vested_Forest'],
                    vals['Unclassed_State_Forest_FD_Acre']]
            if all(x is not None for x in comp) \
                    and vals['Total_Forest_FD_Acre'] is not None:
                s = sum(comp)
                if abs(s - vals['Total_Forest_FD_Acre']) > 0.05:
                    anom('Published forest total does not equal the sum of '
                         'its components',
                         '%s %s: components %.2f vs published %.2f'
                         % (d, fy, s, vals['Total_Forest_FD_Acre']))
            FOREST.append((d, fy, y1, y2, vals, bid))


T84_LAYOUT = {
    'T1.84':  [(1, 2, 2018), (1, 3, 2019), (5, 6, 2020), (8, 9, 2021),
               (11, 12, 2022), (14, 15, 2023)],
    'T1.84b': [(1, 2, 2018), (1, 3, 2019), (5, 6, 2020), (8, 9, 2021),
               (11, 12, 2022), (14, 15, 2023)],
    'T1.84c': [(1, 2, 2018), (1, 3, 2019), (5, 6, 2020), (8, 9, 2021),
               (11, 12, 2022), (14, 15, 2023)],
    'T184d':  [(1, 2, 2018), (1, 3, 2019), (1, 4, 2020), (1, 5, 2021),
               (1, 6, 2022), (1, 7, 2023)],
    'T1.84e': [(1, 2, 2018), (1, 3, 2019), (5, 6, 2020), (8, 9, 2021),
               (11, 12, 2022), (14, 15, 2023)],
}
T84_PARAM = {
    'T1.84': 'Biochemical Oxygen Demand',
    'T1.84b': 'Chemical Oxygen Demand',
    'T1.84c': 'pH',
    'T184d': 'Salinity',
    'T1.84e': 'Dissolved Oxygen',
}
T84_BID = {'T1.84': 'B23', 'T1.84b': 'B25', 'T1.84c': 'B26',
           'T184d': 'B27', 'T1.84e': 'B28'}
T84_HI = {'T1.84': 182, 'T1.84b': 200, 'T1.84c': 200, 'T184d': 195,
          'T1.84e': 196}

WQ_JUNK_PREFIX = ('note', 'source', 'district', 'sl no', 'sl. no',
                  'freshwater', 'marine', 'organic', 'physical', 'chemical',
                  'biochemical', 'dissolved', 'ph/', 'salinity', 'plastic',
                  'amount of', 'concentration', 'total')


def wq_label(v):
    """A station or river label, or None if the cell is header / note text."""
    s = clean_text(v)
    if not s:
        return None
    low = s.lower()
    if low.startswith(WQ_JUNK_PREFIX):
        return None
    try:
        float(s)
        return None
    except ValueError:
        pass
    return s


def is_waterbody(s):
    low = s.lower()
    return low.endswith(('river', 'lake', 'khal', 'canal', 'rivers'))


def parse_t184():
    for sheet, layout in T84_LAYOUT.items():
        bid = T84_BID[sheet]
        par = T84_PARAM[sheet]
        rs = BK.bbs_rows(sheet)
        hi = min(T84_HI[sheet], len(rs))
        for scol, vcol, y in layout:
            body = None
            for i in range(5, hi):
                r = list(rs[i]) + [None] * 20
                lab = wq_label(r[scol])
                if lab is None:
                    continue
                if is_waterbody(lab):
                    body = lab
                    continue
                v, kd = num(r[vcol], '%s %s %d %s' % (bid, lab, y, par))
                seen(bid, v is not None, kd)
                if v is None:
                    continue
                if body is None:
                    anom('Water quality station with no river group header '
                         'above it', '%s %s' % (sheet, lab))
                WQ.append((lab, y, par, v, body, 'Freshwater', bid))


def parse_t184_lakes():
    """Second, independently headed block appended below T1.84."""
    bid = 'B24'
    rs = BK.bbs_rows('T1.84')
    body = None
    for i in range(189, min(205, len(rs))):
        r = list(rs[i]) + [None] * 12
        lab = wq_label(r[2])
        if lab is None:
            continue
        if is_waterbody(lab):
            body = lab
            continue
        for off, y in ((3, 2020), (4, 2021), (5, 2022), (6, 2023)):
            v, kd = num(r[off], '%s %s %d BOD' % (bid, lab, y))
            seen(bid, v is not None, kd)
            if v is not None:
                WQ.append((lab, y, 'Biochemical Oxygen Demand', v, body,
                           'Lake', bid))


T85 = [('B29', 'T1.85', 'Biochemical Oxygen Demand', 12),
       ('B30', 'T1.85b', 'Chemical Oxygen Demand', 12),
       ('B31', 'T1.85c', 'pH', 12),
       ('B32', 'T1.85d', 'Salinity', 12),
       ('B33', 'T1.85e', 'Dissolved Oxygen', 12),
       ('B34', 'T1.85f', 'Plastic and Marine Debris', 14)]
T85_YEARS = [(2, 2019), (3, 2020), (4, 2021), (5, 2022), (6, 2023),
             (7, 2024)]


def parse_t185():
    for bid, sheet, par, hi in T85:
        rs = BK.bbs_rows(sheet)
        for i in range(5, min(hi, len(rs))):
            r = list(rs[i]) + [None] * 12
            lab = wq_label(r[1])
            if lab is None:
                continue
            for c, y in T85_YEARS:
                v, kd = num(r[c], '%s %s %d %s' % (bid, lab, y, par))
                seen(bid, v is not None, kd)
                if v is not None:
                    WQ.append((lab, y, par, v, None, 'Marine', bid))


WASTE_FY = [(2, 5, 2018, 2019), (3, 6, 2019, 2020), (4, 7, 2020, 2021)]


def parse_t314():
    """Only the 'Industry Type' sub-block is in scope."""
    bid = 'B35'
    rs = BK.bbs_rows('T3.14')
    inside = False
    for i in range(4, min(33, len(rs))):
        r = list(rs[i]) + [None] * 10
        lab = clean_text(r[1])
        if lab == 'Industry Type':
            inside = True
            continue
        if lab == 'Category Type':
            inside = False
            continue
        if not inside or not lab:
            continue
        if lab.lower() == 'total':
            anom('Aggregate "Total" row inside the establishment block',
                 'T3.14 row %d' % i)
            continue
        for qc, pc, y1, y2 in WASTE_FY:
            q, k1 = num(r[qc], '%s %s %d-%d qty' % (bid, lab, y1, y2))
            p, k2 = num(r[pc], '%s %s %d-%d pct' % (bid, lab, y1, y2))
            seen(bid, q is not None, k1)
            if q is None and p is None:
                continue
            EST.append((lab, y1, y2, q, p, bid))


def parse_t322():
    bid = 'B36'
    rs = BK.bbs_rows('T3.22')
    for i in range(4, min(7, len(rs))):
        r = list(rs[i]) + [None] * 10
        lab = clean_text(r[1])
        if not lab or lab.lower().startswith('source'):
            continue
        for qc, pc, y1, y2 in WASTE_FY:
            q, k1 = num(r[qc], '%s %s %d-%d produced' % (bid, lab, y1, y2))
            p, k2 = num(r[pc], '%s %s %d-%d reused' % (bid, lab, y1, y2))
            seen(bid, q is not None, k1)
            if q is None and p is None:
                continue
            IND.append((lab, y1, y2, q, p, bid))
    if len(IND) <= 3:
        anom('Source sheet T3.22 publishes only one category row, so '
             'Industrial_Type is loaded with a single industry and '
             'Industry_Usage with one row per fiscal year',
             '%d row(s) present' % (len(IND) // 3 if IND else 0))
    anom('T3.22 labels reused waste water as a percentage although its values '
         'are outside the percentage range and the table title states '
         'thousand litres',
         'The published values are preserved as reused waste water; a '
         'separate database view calculates the reuse rate for review')


def parse_bmd_temp():
    for i in range(1, 19):
        sheet = 'Table-%d' % i
        bid = 'B%02d' % (36 + i)
        rs = BK.bmd_temp_rows(sheet)
        title = clean_text(rs[0][0]) if rs else ''
        m = None
        for tok in title.replace('(', ' ').replace(')', ' ').split():
            if tok.isdigit() and 1900 <= int(tok) <= 2100:
                m = int(tok)
        if m is None:
            anom('BMD temperature sheet with no year in its title', sheet)
            continue
        for r in rs[2:]:
            r = list(r) + [None] * 26
            st = canon_station(r[0])
            if st is None:
                continue
            for k in range(12):
                v, kd = num(r[1 + k], '%s %s %d-%02d max' % (bid, st, m, k + 1))
                seen(bid, v is not None, kd)
                if v is not None:
                    TEMP.append((st, m, k + 1, 'Maximum', v, bid))
                v, kd = num(r[13 + k],
                            '%s %s %d-%02d min' % (bid, st, m, k + 1))
                seen(bid, v is not None, kd)
                if v is not None:
                    TEMP.append((st, m, k + 1, 'Minimum', v, bid))


def parse_bmd_sun():
    for bid, sheet in (('B55', 'Climate '),
                       ('B56', 'Climate Leap year February')):
        rs = BK.bmd_sun_rows(sheet)
        n = 0
        for r in rs[1:]:
            r = list(r) + [None] * 36
            n += 1
        anom('BMD Sunshine.xls carries Station ID 0.0 on every row and no '
             'station name, so its rows cannot be attached to a Station',
             '%s: %d data rows unattachable' % (sheet, n))
        DROPPED_BLOCK[bid] = ('BMD Sunshine.xls / %s' % sheet, n,
                              'Station identifier is 0.0 on every row and no '
                              'station name column exists. Sunshine_Record '
                              'has Station_Name in its primary key, so no row '
                              'can be inserted without inventing a station.')


DROPPED_BLOCK = {}


BRRI_TARGET = {'Max_Temp': ('temp', 'Maximum'), 'Min_Temp': ('temp', 'Minimum'),
               'Rainfall': ('rain', None), 'Humidity': ('hum', None),
               'Sunshine': ('sun', None)}
BRRI_BID = {'Max_Temp': 'B57', 'Min_Temp': 'B58', 'Rainfall': 'B59',
            'Humidity': 'B60', 'Sunshine': 'B61'}
BRRI_DAILY = collections.defaultdict(list)


def parse_brri():
    for tag, (kind, typ) in BRRI_TARGET.items():
        bid = BRRI_BID[tag]
        rs = BK.brri_rows(tag)
        for r in rs[2:]:
            r = list(r) + [None] * 36
            st = canon_station(r[0])
            y = as_int(r[1])
            m = month_no(r[2])
            if st is None or y is None or m is None:
                continue
            if not 1900 <= y <= 2100:
                continue
            for d in range(1, 32):
                v, kd = num(r[2 + d], '%s %s %d-%02d-%02d' % (bid, st, y, m, d),
                            allow_trace=(kind == 'rain'))
                seen(bid, v is not None, kd)
                if v is None:
                    continue
                if not valid_day(y, m, d, '%s %s' % (bid, st)):
                    continue
                if kind == 'sun':
                    SUN.append((st, y, m, d, v, bid))
                else:
                    BRRI_DAILY[(tag, st, y, m)].append(v)


def aggregate_brri():
    """Daily BRRI readings become monthly rows, because the approved schema
    keeps temperature, humidity and rainfall at month grain."""
    for (tag, st, y, m), vals in BRRI_DAILY.items():
        if not vals:
            continue
        kind, typ = BRRI_TARGET[tag]
        bid = BRRI_BID[tag]
        if kind == 'rain':
            v = sum(vals)
            RAIN.append((st, y, m, v, bid))
        elif kind == 'hum':
            v = sum(vals) / len(vals)
            HUM.append((st, y, m, round(v, 2), bid))
        elif kind == 'temp':
            v = sum(vals) / len(vals)
            TEMP.append((st, y, m, typ, round(v, 2), bid))
        if len(vals) < 25:
            anom('Month aggregated from fewer than 25 daily readings',
                 '%s %s %d-%02d: %d days' % (tag, st, y, m, len(vals)))
    anom('BRRI daily readings aggregated to month grain to match the '
         'approved schema',
         '%d station-months formed' % len(BRRI_DAILY))


def parse_rivers():
    rs = BK.rivers_rows()
    for r in rs[1:]:
        r = list(r) + [None] * 6
        nm = clean_text(r[1])
        if not nm:
            continue
        RIVREG.append((as_int(r[0]), nm, clean_text(r[2]), clean_text(r[3]),
                       clean_text(r[4])))


def parse_gw():
    for i, sheet in enumerate(('Table-2', 'Table-3', 'Table-4', 'Table-5',
                               'Table-6', 'Table-7')):
        bid = 'B%d' % (63 + i)
        rs = BK.bwdb_gw_rows(sheet)
        dist = None
        sub = None
        for r in rs[2:]:
            r = list(r) + [None] * 10
            wno = as_int(r[0])
            wid = clean_text(r[1])
            if wno is None or not wid:
                continue
            d = canon_district(r[5])
            if d:
                dist = d
                s = clean_text(r[6])
                sub = s if s else None
            if dist is None:
                anom('Groundwater well before the first district label',
                     '%s well %s' % (sheet, wid))
                continue
            lon, k1 = num(r[2], '%s %s long' % (bid, wid))
            lat, k2 = num(r[3], '%s %s lat' % (bid, wid))
            seen(bid, True, k1)
            up = clean_text(r[4]) or None
            GW.append((dist, wno, wid, lat, lon, sub, up, bid))
    if any(g[5] and g[5] != g[5][::-1] for g in GW):
        pass
    for g in GW:
        if g[5] and g[5][::-1] in ('Kumilla', 'Dhaka', 'Faridpur'):
            anom('Sub-Division value stored with its characters reversed',
                 '%s -> %s' % (g[5], g[5][::-1]))


T102_YEARHEADS = [(2, 2017), (14, 2018), (26, 2019), (38, 2020), (50, 2021),
                  (62, 2022), (74, 2023), (86, 2024)]


def run_parsers():
    parse_rowform_month('B01', 'T1.02', 0, 248, 2, 'temp', 'Minimum')
    parse_wide_year_blocks('B02', 'T1.02', 256, 292, 1, T102_YEARHEADS,
                           'Minimum')
    parse_rowform_month('B03', 'T1.03', 0, 249, 2, 'temp', 'Maximum')
    parse_wide_year_blocks('B04', 'T1.03', 258, 294, 1, T102_YEARHEADS,
                           'Maximum')
    parse_colform_year('B05', 'T1.05', 3, 144, 1, 2, 3, 'rain', 15,
                       'Annual rainfall')
    parse_colform_year('B06', 'T1.05', 150, 326, 1, 2, 3, 'rain', 15,
                       'Annual rainfall')
    parse_colform_year('B07', 'T1.05', 332, 510, 1, 2, 3, 'rain', 15,
                       'Annual rainfall')
    parse_colform_year('B08', 'T1.06', 3, 148, 1, 2, 3, 'hum', 15,
                       'Annual humidity')
    parse_colform_year('B09', 'T1.06', 154, 330, 1, 2, 3, 'hum', 15,
                       'Annual humidity')
    parse_colform_year('B10', 'T1.06', 337, 515, 1, 2, 3, 'hum', 15,
                       'Annual humidity')
    parse_rowform_wind('B11', 'T1.08', 0, 393, 'Minimum')
    parse_rowform_wind('B12', 'T1.10', 0, 244, 'Maximum')
    parse_rowform_wind('B13', 'T1.10', 245, 572, 'Maximum')
    parse_colform_year('B20', 'T1.19', 3, 354, 1, 2, 3, 'thunder')
    parse_colform_year('B21', 'T1.19 a', 3, 354, 1, 2, 3, 'lightning')
    parse_t113()
    parse_t114()
    parse_t166()
    parse_t184()
    parse_t184_lakes()
    parse_t185()
    parse_t314()
    parse_t322()
    parse_bmd_temp()
    parse_bmd_sun()
    parse_brri()
    aggregate_brri()
    parse_rivers()
    parse_gw()
    range_check()


PLAUSIBLE = {
    'Temperature': (-5.0, 50.0,
                    'the national record runs from about 2 to 45 degrees '
                    'Celsius'),
    'Humidity': (0.0, 100.0,
                 'relative humidity is a percentage and cannot exceed 100'),
    'Rainfall': (0.0, 3000.0,
                 'the wettest recorded month in Bangladesh is below 3000 '
                 'millimetres'),
    'Sunshine': (0.0, 14.0,
                 'the longest day at this latitude is close to 13 hours and '
                 '30 minutes, so a day cannot hold more than 14 hours of '
                 'bright sunshine'),
    'Wind Speed': (0.0, 250.0,
                   'the strongest cyclone wind recorded over Bangladesh is '
                   'below 250 knots'),
    'Wind Direction': (0.0, 360.0, 'a compass bearing lies in 0 to 360'),
}


def in_range(measure, v, ctx):
    if v is None:
        return True
    lo, hi, why = PLAUSIBLE[measure]
    if lo <= v <= hi:
        return True
    anom('%s value outside the plausible range %g to %g, because %s'
         % (measure, lo, hi, why), '%s = %g' % (ctx, v))
    return False


def range_check():
    global TEMP, HUM, RAIN, SUN, WIND

    def ctx(b, st, *rest):
        return '%s %s %s' % (b, st, '-'.join(str(x) for x in rest))

    TEMP = [r for r in TEMP
            if in_range('Temperature', r[4], ctx(r[5], r[0], r[1], r[2], r[3]))]
    HUM = [r for r in HUM
           if in_range('Humidity', r[3], ctx(r[4], r[0], r[1], r[2]))]
    RAIN = [r for r in RAIN
            if in_range('Rainfall', r[3], ctx(r[4], r[0], r[1], r[2]))]
    SUN = [r for r in SUN
           if in_range('Sunshine', r[4], ctx(r[5], r[0], r[1], r[2], r[3]))]
    kept = []
    for st, y, m, ty, sp, di, b in WIND:
        c = ctx(b, st, y, m, ty)
        if not in_range('Wind Speed', sp, c + ' speed'):
            sp = None
        if not in_range('Wind Direction', di, c + ' direction'):
            di = None
        if sp is not None or di is not None:
            kept.append((st, y, m, ty, sp, di, b))
    WIND = kept


SRC_ORG = {}


def build_source_index():
    for b in BK.BLOCKS:
        SRC_ORG[b['id']] = (b['org'], b['file'], b['sheet'].strip())


MEASURE_UNIT = [
    ('Temperature', 'Degree Celsius', 'Temperature_Record.Temp'),
    ('Humidity', 'Percent', 'Humidity_Record.Humidity'),
    ('Rainfall', 'Millimetre', 'Rainfall_Record.Rainfall'),
    ('Wind Speed', 'Knot', 'Wind_Record.Wind_Speed'),
    ('Wind Direction', 'Degree', 'Wind_Record.Direction'),
    ('Thunderstorm', 'Count of days in the month',
     'Climatic_Event_Record.Thunderstorm'),
    ('Lightning', 'Count of days in the month',
     'Climatic_Event_Record.Lightning'),
    ('Sunshine', 'Hour', 'Sunshine_Record.Sunshine_Hours'),
    ('Radiation', 'Langley per hour', 'Radiation_Record.Radiation'),
    ('Biochemical Oxygen Demand', 'Milligram per litre', 'Water_Quality.Value'),
    ('Chemical Oxygen Demand', 'Milligram per litre', 'Water_Quality.Value'),
    ('Dissolved Oxygen', 'Milligram per litre', 'Water_Quality.Value'),
    ('pH', 'pH unit (dimensionless)', 'Water_Quality.Value'),
    ('Salinity', 'Parts per thousand', 'Water_Quality.Value'),
    ('Plastic and Marine Debris', 'Piece', 'Water_Quality.Value'),
    ('Forest Area', 'Acre', 'Forest_Area_Record'),
    ('Waste Water', 'Cubic metre', 'Type_Of_Establishments.Quantity'),
    ('Produced Waste Water', 'Thousand litre',
     'Industry_Usage.Produced_Waste_Water'),
    ('Reused Waste Water', 'Thousand litre',
     'Industry_Usage.Reused_Waste_Water'),
]


ORG_RANK = {'BBS': 1, 'BMD': 2, 'BRRI': 3, 'BWDB': 1}
CONFLICTS = []
DUP_IDENTICAL = collections.Counter()
CONFLICT_CLASS = collections.Counter()

ROUNDING_TOLERANCE = {
    'Temperature_Record': 0.1,
    'Humidity_Record': 0.5,
    'Rainfall_Record': 0.5,
    'Sunshine_Record': 0.1,
    'Wind_Record': 0.5,
    'Water_Quality': 0.05,
}


def fmtvals(vals):
    return ', '.join('' if v is None else str(v) for v in vals)


def conflict_class(relation, kept, lost):
    """'rounding' when the two values agree to within the tolerance."""
    tol = ROUNDING_TOLERANCE.get(relation)
    if tol is None:
        return 'substantive'
    try:
        a = [float(x) for x in kept]
        b = [float(x) for x in lost]
    except (TypeError, ValueError):
        return 'substantive'
    if len(a) != len(b) or not a:
        return 'substantive'
    return 'rounding' if all(abs(x - y) <= tol for x, y in zip(a, b)) \
        else 'substantive'


def log_conflict(relation, key, korg, kvals, lorg, lvals):
    cls = conflict_class(relation, kvals, lvals)
    CONFLICT_CLASS[(relation, '%s over %s' % (korg, lorg), cls)] += 1
    CONFLICTS.append((relation, ' | '.join(str(k) for k in key), korg,
                      fmtvals(kvals), lorg, fmtvals(lvals), cls))


def resolve(relation, rows, keylen, vallen):
    """rows are tuples ending in the block id. Returns deduplicated rows."""
    best = {}
    for r in rows:
        key = tuple(r[:keylen])
        bid = r[-1]
        org = SRC_ORG.get(bid, ('?',))[0]
        vals = tuple(r[keylen:keylen + vallen])
        cur = best.get(key)
        if cur is None:
            best[key] = (r, org, vals)
            continue
        crow, corg, cvals = cur
        if vals == cvals:
            DUP_IDENTICAL[relation] += 1
            continue
        if ORG_RANK.get(org, 9) < ORG_RANK.get(corg, 9):
            log_conflict(relation, key, org, vals, corg, cvals)
            best[key] = (r, org, vals)
        else:
            log_conflict(relation, key, corg, cvals, org, vals)
    return [v[0] for v in best.values()]


def keysort(rows, n):
    def k(r):
        return tuple((0, v) if isinstance(v, (int, float)) else (1, str(v))
                     for v in r[:n])
    return sorted(rows, key=k)


ONE_NF = {}


def build_1nf():
    ONE_NF['Climate_Observation_1NF'] = (
        ['Station_Name', 'Year', 'Month', 'Measure', 'Type', 'Value',
         'Source_Organization', 'Source_File', 'Source_Sheet', 'Block'],
        [])
    a = ONE_NF['Climate_Observation_1NF'][1]
    for st, y, m, ty, v, b in TEMP:
        o, f, s = SRC_ORG[b]
        a.append([st, y, m, 'Temperature', ty, v, o, f, s, b])
    for st, y, m, v, b in HUM:
        o, f, s = SRC_ORG[b]
        a.append([st, y, m, 'Humidity', '', v, o, f, s, b])
    for st, y, m, v, b in RAIN:
        o, f, s = SRC_ORG[b]
        a.append([st, y, m, 'Rainfall', '', v, o, f, s, b])
    for st, y, m, ty, sp, di, b in WIND:
        o, f, s = SRC_ORG[b]
        if sp is not None:
            a.append([st, y, m, 'Wind Speed', ty, sp, o, f, s, b])
        if di is not None:
            a.append([st, y, m, 'Wind Direction', ty, di, o, f, s, b])
    for st, y, m, th, li, b in EVENT:
        o, f, s = SRC_ORG[b]
        if th is not None:
            a.append([st, y, m, 'Thunderstorm', '', th, o, f, s, b])
        if li is not None:
            a.append([st, y, m, 'Lightning', '', li, o, f, s, b])

    ONE_NF['Daily_Observation_1NF'] = (
        ['Station_Name', 'Year', 'Month', 'Day', 'Sample_No', 'Measure',
         'Value', 'Source_Organization', 'Source_Sheet', 'Block'], [])
    a = ONE_NF['Daily_Observation_1NF'][1]
    for st, y, m, d, v, b in SUN:
        o, f, s = SRC_ORG[b]
        a.append([st, y, m, d, '', 'Sunshine Hours', v, o, s, b])
    for st, y, m, d, h, v, b in RAD:
        o, f, s = SRC_ORG[b]
        a.append([st, y, m, d, h, 'Radiation', v, o, s, b])

    ONE_NF['Water_Quality_1NF'] = (
        ['WQ_Station_Name', 'River_Name', 'Water_Category', 'Year',
         'Parameter_Type', 'Value', 'Source_Organization', 'Source_Sheet',
         'Block'], [])
    a = ONE_NF['Water_Quality_1NF'][1]
    for st, y, par, v, riv, cat, b in WQ:
        o, f, s = SRC_ORG[b]
        a.append([st, riv or '', cat, y, par, v, o, s, b])

    ONE_NF['Forest_Area_1NF'] = (
        ['District_Name', 'Fiscal_Year', 'Fiscal_Start_Year',
         'Fiscal_End_Year', 'Measure', 'Acre', 'Source_Sheet', 'Block'], [])
    a = ONE_NF['Forest_Area_1NF'][1]
    for d, fy, y1, y2, vals, b in FOREST:
        o, f, s = SRC_ORG[b]
        for attr, _ in FOREST_MEASURES:
            if vals[attr] is not None:
                a.append([d, fy, y1, y2, attr, vals[attr], s, b])

    ONE_NF['Ground_Water_Well_1NF'] = (
        ['District_Name', 'Well_No', 'Well_ID', 'Latitude', 'Longitude',
         'Sub_Division', 'Upazilla', 'Source_Sheet', 'Block'], [])
    a = ONE_NF['Ground_Water_Well_1NF'][1]
    for d, wn, wid, la, lo, sub, up, b in GW:
        o, f, s = SRC_ORG[b]
        a.append([d, wn, wid, la, lo, sub or '', up or '', s, b])

    ONE_NF['Waste_Water_1NF'] = (
        ['Category', 'Group_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year',
         'Reported_Value_1', 'Reported_Value_2', 'Source_Sheet', 'Block'], [])
    a = ONE_NF['Waste_Water_1NF'][1]
    for nm, y1, y2, q, p, b in EST:
        o, f, s = SRC_ORG[b]
        a.append(['Type of Establishment', nm, y1, y2, q, p, s, b])
    for nm, y1, y2, q, p, b in IND:
        o, f, s = SRC_ORG[b]
        a.append(['Industry', nm, y1, y2, q, p, s, b])

    ONE_NF['River_Register_1NF'] = (
        ['Serial_No', 'River_Name', 'BWDB_Zone', 'Border_River', 'Flow_Type'],
        [list(r) for r in RIVREG])


TWO_NF = {}


def build_2nf():
    rows = []
    for b in BK.BLOCKS:
        rows.append([b['id'], b['org'], b['file'], b['sheet'].strip(),
                     b['title'], b['rep'], b['target']])
    TWO_NF['Source_Block_2NF'] = (
        ['Block', 'Organization', 'Source_File', 'Source_Sheet', 'Block_Title',
         'Repeating_Group_Removed', 'Target_Relation'], rows)

    TWO_NF['Measure_Unit_2NF'] = (
        ['Measure', 'Unit', 'Carried_By'],
        [list(r) for r in MEASURE_UNIT])

    hdr = ['Station_Name', 'Year', 'Month', 'Measure', 'Type', 'Value',
           'Block']
    rows = [[r[0], r[1], r[2], r[3], r[4], r[5], r[9]]
            for r in ONE_NF['Climate_Observation_1NF'][1]]
    TWO_NF['Climate_Observation_2NF'] = (hdr, rows)

    hdr = ['Station_Name', 'Year', 'Month', 'Day', 'Sample_No', 'Measure',
           'Value', 'Block']
    rows = [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[9]]
            for r in ONE_NF['Daily_Observation_1NF'][1]]
    TWO_NF['Daily_Observation_2NF'] = (hdr, rows)

    st_riv = {}
    multi = collections.defaultdict(set)
    for st, y, par, v, riv, cat, b in WQ:
        if riv:
            multi[st].add(riv)
            st_riv.setdefault(st, (riv, cat))
    for st, rivs in multi.items():
        if len(rivs) > 1:
            anom('Water quality station listed under more than one river',
                 '%s -> %s' % (st, sorted(rivs)))
    marine = sorted({st for st, y, par, v, riv, cat, b in WQ
                     if not riv and cat == 'Marine'})
    for st in marine:
        if st not in st_riv:
            st_riv[st] = ('Bay of Bengal', 'Marine')
    if marine:
        anom('Marine monitoring point stands in the sea, so the source names '
             'no river. The water body is recorded as Bay of Bengal so the '
             'reading keeps a valid parent row',
             '%d stations: %s' % (len(marine), ', '.join(marine[:4])))
    TWO_NF['River_Station_2NF'] = (
        ['WQ_Station_Name', 'River_Name', 'Water_Category'],
        [[st, rv, cat] for st, (rv, cat) in sorted(st_riv.items())])
    TWO_NF['Water_Quality_2NF'] = (
        ['WQ_Station_Name', 'Year', 'Parameter_Type', 'Value', 'Block'],
        [[r[0], r[3], r[4], r[5], r[8]]
         for r in ONE_NF['Water_Quality_1NF'][1]])

    fy = sorted({(r[2], r[3], r[1]) for r in ONE_NF['Forest_Area_1NF'][1]})
    TWO_NF['Fiscal_Year_2NF'] = (
        ['Start_Year', 'End_Year', 'Published_As'], [list(x) for x in fy])
    TWO_NF['Forest_Area_2NF'] = (
        ['District_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year', 'Measure',
         'Acre', 'Block'],
        [[r[0], r[2], r[3], r[4], r[5], r[7]]
         for r in ONE_NF['Forest_Area_1NF'][1]])

    TWO_NF['Ground_Water_Well_2NF'] = ONE_NF['Ground_Water_Well_1NF']
    TWO_NF['Waste_Water_2NF'] = ONE_NF['Waste_Water_1NF']
    TWO_NF['River_Register_2NF'] = ONE_NF['River_Register_1NF']


THREE_NF = {}


def build_3nf():
    src = TWO_NF['Climate_Observation_2NF'][1]

    def pick(measure, typed):
        out = []
        for r in src:
            if r[3] != measure:
                continue
            out.append(r)
        return out

    t = [[r[0], r[1], r[2], r[4], r[5], r[6]] for r in pick('Temperature', 1)]
    THREE_NF['Temperature_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Type', 'Temp', 'Block'], t)

    h = [[r[0], r[1], r[2], r[5], r[6]] for r in pick('Humidity', 0)]
    THREE_NF['Humidity_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Humidity', 'Block'], h)

    ra = [[r[0], r[1], r[2], r[5], r[6]] for r in pick('Rainfall', 0)]
    THREE_NF['Rainfall_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Rainfall', 'Block'], ra)

    w = {}
    for r in src:
        if r[3] not in ('Wind Speed', 'Wind Direction'):
            continue
        k = (r[0], r[1], r[2], r[4], r[6])
        e = w.setdefault(k, [None, None])
        e[0 if r[3] == 'Wind Speed' else 1] = r[5]
    THREE_NF['Wind_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Type', 'Wind_Speed', 'Direction',
         'Block'],
        [[k[0], k[1], k[2], k[3], v[0], v[1], k[4]] for k, v in w.items()])

    e = {}
    for r in src:
        if r[3] not in ('Thunderstorm', 'Lightning'):
            continue
        k = (r[0], r[1], r[2])
        rec = e.setdefault(k, [None, None, r[6]])
        rec[0 if r[3] == 'Thunderstorm' else 1] = r[5]
    THREE_NF['Climatic_Event_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Thunderstorm', 'Lightning',
         'Block'],
        [[k[0], k[1], k[2], v[0], v[1], v[2]] for k, v in e.items()])

    d = TWO_NF['Daily_Observation_2NF'][1]
    THREE_NF['Sunshine_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Day', 'Sunshine_Hours', 'Block'],
        [[r[0], r[1], r[2], r[3], r[6], r[7]] for r in d
         if r[5] == 'Sunshine Hours'])
    THREE_NF['Radiation_Record_3NF'] = (
        ['Station_Name', 'Year', 'Month', 'Day', 'Sample_No', 'Radiation',
         'Block'],
        [[r[0], r[1], r[2], r[3], r[4], r[6], r[7]] for r in d
         if r[5] == 'Radiation'])

    THREE_NF['Water_Quality_3NF'] = TWO_NF['Water_Quality_2NF']

    f = {}
    for r in TWO_NF['Forest_Area_2NF'][1]:
        k = (r[0], r[1], r[2])
        f.setdefault(k, {})[r[3]] = r[4]
    hdr = ['District_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year'] + \
          [a for a, _ in FOREST_MEASURES]
    THREE_NF['Forest_Area_Record_3NF'] = (
        hdr, [[k[0], k[1], k[2]] + [v.get(a) for a, _ in FOREST_MEASURES]
              for k, v in f.items()])

    dsub = {}
    for r in TWO_NF['Ground_Water_Well_2NF'][1]:
        if r[5]:
            dsub[r[0]] = r[5]
    THREE_NF['District_Sub_Division_3NF'] = (
        ['District_Name', 'Sub_Division'],
        [[k, v] for k, v in sorted(dsub.items())])
    THREE_NF['Ground_Water_Well_3NF'] = (
        ['District_Name', 'Well_No', 'Well_ID', 'Latitude', 'Longitude',
         'Upazilla'],
        [[r[0], r[1], r[2], r[3], r[4], r[6]]
         for r in TWO_NF['Ground_Water_Well_2NF'][1]])

    est = [r for r in TWO_NF['Waste_Water_2NF'][1]
           if r[0] == 'Type of Establishment']
    ind = [r for r in TWO_NF['Waste_Water_2NF'][1] if r[0] == 'Industry']
    THREE_NF['Type_Of_Establishments_3NF'] = (
        ['Size_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year', 'Quantity',
         'Percentage'],
        [[r[1], r[2], r[3], r[4], r[5]] for r in est])
    THREE_NF['Industry_Usage_3NF'] = (
        ['Industry_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year',
         'Produced_Waste_Water', 'Reused_Waste_Water'],
        [[r[1], r[2], r[3], r[4], r[5]] for r in ind])
    THREE_NF['River_Register_3NF'] = TWO_NF['River_Register_2NF']
    THREE_NF['River_Station_3NF'] = TWO_NF['River_Station_2NF']
    THREE_NF['Fiscal_Year_3NF'] = TWO_NF['Fiscal_Year_2NF']


BCNF = {}
PK = {}
FK = {}
ROWCOUNT = {}


def build_bcnf():
    t = resolve('Temperature_Record', [tuple(r) for r in
                                       THREE_NF['Temperature_Record_3NF'][1]],
                4, 1)
    BCNF['Temperature_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Type', 'Temp'],
        [list(r[:5]) for r in keysort(t, 4)])
    PK['Temperature_Record'] = '(Station_Name, Year, Month, Type)'

    h = resolve('Humidity_Record',
                [tuple(r) for r in THREE_NF['Humidity_Record_3NF'][1]], 3, 1)
    BCNF['Humidity_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Humidity'],
        [list(r[:4]) for r in keysort(h, 3)])
    PK['Humidity_Record'] = '(Station_Name, Year, Month)'

    ra = resolve('Rainfall_Record',
                 [tuple(r) for r in THREE_NF['Rainfall_Record_3NF'][1]], 3, 1)
    BCNF['Rainfall_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Rainfall'],
        [list(r[:4]) for r in keysort(ra, 3)])
    PK['Rainfall_Record'] = '(Station_Name, Year, Month)'

    w = resolve('Wind_Record',
                [tuple(r) for r in THREE_NF['Wind_Record_3NF'][1]], 4, 2)
    BCNF['Wind_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Type', 'Wind_Speed', 'Direction'],
        [list(r[:6]) for r in keysort(w, 4)])
    PK['Wind_Record'] = '(Station_Name, Year, Month, Type)'

    e = resolve('Climatic_Event_Record',
                [tuple(r) for r in THREE_NF['Climatic_Event_Record_3NF'][1]],
                3, 2)
    BCNF['Climatic_Event_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Thunderstorm', 'Lightning'],
        [list(r[:5]) for r in keysort(e, 3)])
    PK['Climatic_Event_Record'] = '(Station_Name, Year, Month)'

    s = resolve('Sunshine_Record',
                [tuple(r) for r in THREE_NF['Sunshine_Record_3NF'][1]], 4, 1)
    BCNF['Sunshine_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Day', 'Sunshine_Hours'],
        [list(r[:5]) for r in keysort(s, 4)])
    PK['Sunshine_Record'] = '(Station_Name, Year, Month, Day)'

    rd = resolve('Radiation_Record',
                 [tuple(r) for r in THREE_NF['Radiation_Record_3NF'][1]], 5, 1)
    BCNF['Radiation_Record'] = (
        ['Station_Name', 'Year', 'Month', 'Day', 'Sample_No', 'Radiation'],
        [list(r[:6]) for r in keysort(rd, 5)])
    PK['Radiation_Record'] = '(Station_Name, Year, Month, Day, Sample_No)'

    q = resolve('Water_Quality',
                [tuple(r) for r in THREE_NF['Water_Quality_3NF'][1]], 3, 1)
    BCNF['Water_Quality'] = (
        ['WQ_Station_Name', 'Year', 'Parameter_Type', 'Value'],
        [list(r[:4]) for r in keysort(q, 3)])
    PK['Water_Quality'] = '(WQ_Station_Name, Year, Parameter_Type)'

    fr = resolve('Forest_Area_Record',
                 [tuple(r) + ('B22',) for r in
                  THREE_NF['Forest_Area_Record_3NF'][1]], 3, 8)
    hdr = ['District_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year',
           'Protected_Area', 'Unclassed_State_Forest_FD_Acre',
           'Unclassed_State_Forest_Admin_Acre',
           'Reserved_Forest_Section_20_Acre',
           'Reserved_Forest_Section_4_6_Acre', 'Acquired_Vested_Forest',
           'Total_Forest_FD_Acre', 'Total_Forest_Land']
    order = [a for a, _ in FOREST_MEASURES]
    rows = []
    for r in keysort(fr, 3):
        d = dict(zip(order, r[3:11]))
        rows.append([r[0], r[1], r[2], d['Protected_Area'],
                     d['Unclassed_State_Forest_FD_Acre'],
                     d['Unclassed_State_Forest_Admin_Acre'],
                     d['Reserved_Forest_Section_20_Acre'],
                     d['Reserved_Forest_Section_4_6_Acre'],
                     d['Acquired_Vested_Forest'], d['Total_Forest_FD_Acre'],
                     d['Total_Forest_Land']])
    BCNF['Forest_Area_Record'] = (hdr, rows)
    PK['Forest_Area_Record'] = \
        '(District_Name, Fiscal_Start_Year, Fiscal_End_Year)'

    anom('The approved diagram has no groundwater entity, so the wells '
         'reconciled at Third Normal Form have no relation to load into',
         '%d wells from %d districts stop at Third Normal Form'
         % (len(THREE_NF['Ground_Water_Well_3NF'][1]),
            len({r[0] for r in THREE_NF['Ground_Water_Well_3NF'][1]})))

    BCNF['Type_Of_Establishments'] = (
        ['Size_Name', 'Start_Year', 'End_Year', 'Quantity', 'Percentage'],
        [[r[0], r[1], r[2], r[3], r[4]]
         for r in keysort(THREE_NF['Type_Of_Establishments_3NF'][1], 3)])
    PK['Type_Of_Establishments'] = '(Size_Name, Start_Year, End_Year)'
    BCNF['Industry_Usage'] = (
        ['Industry_Name', 'Start_Year', 'End_Year',
         'Produced_Waste_Water', 'Reused_Waste_Water'],
        [[r[0], r[1], r[2], r[3], r[4]]
         for r in keysort(THREE_NF['Industry_Usage_3NF'][1], 3)])
    PK['Industry_Usage'] = '(Industry_Name, Start_Year, End_Year)'
    BCNF['Size'] = (
        ['Size_Name'],
        [[s] for s in sorted({r[0] for r in
                              BCNF['Type_Of_Establishments'][1]})])
    PK['Size'] = 'Size_Name'
    BCNF['Industrial_Type'] = (
        ['Industry_Name'],
        [[s] for s in sorted({r[0] for r in BCNF['Industry_Usage'][1]})])
    PK['Industrial_Type'] = 'Industry_Name'
    anom('Both waste relations are keyed by fiscal year in the approved '
         'diagram, so every published year loads rather than only the latest',
         'Type_Of_Establishments %d rows over %d fiscal years; Industry_Usage '
         '%d rows over %d'
         % (len(BCNF['Type_Of_Establishments'][1]),
            len({(r[1], r[2]) for r in BCNF['Type_Of_Establishments'][1]}),
            len(BCNF['Industry_Usage'][1]),
            len({(r[1], r[2]) for r in BCNF['Industry_Usage'][1]})))

    stations = set()
    for rel in ('Temperature_Record', 'Humidity_Record', 'Rainfall_Record',
                'Wind_Record', 'Climatic_Event_Record', 'Sunshine_Record',
                'Radiation_Record'):
        for r in BCNF[rel][1]:
            stations.add(r[0])
    BCNF['Station'] = (['Station_Name'], [[s] for s in sorted(stations)])
    PK['Station'] = 'Station_Name'

    districts = set()
    for r in BCNF['Forest_Area_Record'][1]:
        districts.add(r[0])
    BCNF['District'] = (['District_Name'], [[d] for d in sorted(districts)])
    PK['District'] = 'District_Name'

    reg = {}
    for ser, nm, zone, border, flow in RIVREG:
        reg[river_key(nm)] = nm
    rivers = {nm for _, nm, _, _, _ in RIVREG}
    stmap = {}
    unmatched = {}
    for st, rv, cat in THREE_NF['River_Station_3NF'][1]:
        k = river_key(rv)
        target = reg.get(k)
        if target is None:
            alias = RIVER_ALIAS.get(k)
            if alias and river_key(alias) in reg:
                target = reg[river_key(alias)]
                RIVER_MAP_LOG[rv] = target
        if target is None and cat == 'Marine':
            target = rv
            rivers.add(rv)
        elif target is None:
            unmatched[rv] = unmatched.get(rv, 0) + 1
            target = rv
            rivers.add(rv)
            anom('River or lake name published by BBS that is absent from the '
                 'BWDB river register', rv)
        elif target != rv:
            RIVER_MAP_LOG[rv] = target
        stmap[st] = target
    BCNF['River'] = (['River_Name'], [[r] for r in sorted(rivers)])
    PK['River'] = 'River_Name'
    BCNF['River_Station'] = (
        ['WQ_Station_Name', 'River_Name'],
        [[st, rv] for st, rv in sorted(stmap.items())])
    PK['River_Station'] = 'WQ_Station_Name'
    c = collections.Counter(r[0] for r in BCNF['River_Station'][1])
    bad = [k for k, v in c.items() if v > 1]
    if bad:
        anom('Water quality station name repeats across rivers, so the single '
             'column foreign key from Water_Quality is invalid', str(bad[:5]))
    else:
        anom('Every water quality station name is unique in River_Station, so '
             'WQ_Station_Name is the relation primary key and the single '
             'column foreign key from Water_Quality is valid',
             '%d stations verified' % len(c))

    years, months, days = set(), set(), set()
    for rel in ('Temperature_Record', 'Humidity_Record', 'Rainfall_Record',
                'Wind_Record', 'Climatic_Event_Record'):
        for r in BCNF[rel][1]:
            years.add(r[1])
            months.add((r[1], r[2]))
    for rel in ('Sunshine_Record', 'Radiation_Record'):
        for r in BCNF[rel][1]:
            years.add(r[1])
            months.add((r[1], r[2]))
            days.add((r[1], r[2], r[3]))
    for r in BCNF['Water_Quality'][1]:
        years.add(r[1])
    for r in BCNF['Forest_Area_Record'][1]:
        years.add(r[1])
        years.add(r[2])
    for rel in ('Type_Of_Establishments', 'Industry_Usage'):
        for r in BCNF[rel][1]:
            years.add(r[1])
            years.add(r[2])
    BCNF['Year_Time'] = (['Year'], [[y] for y in sorted(years)])
    PK['Year_Time'] = 'Year'
    BCNF['Month_Time'] = (['Year', 'Month'],
                          [list(x) for x in sorted(months)])
    PK['Month_Time'] = '(Year, Month)'
    BCNF['Day_Time'] = (['Year', 'Month', 'Day'],
                        [list(x) for x in sorted(days)])
    PK['Day_Time'] = '(Year, Month, Day)'
    fy = {(r[1], r[2]) for r in BCNF['Forest_Area_Record'][1]}
    for rel in ('Type_Of_Establishments', 'Industry_Usage'):
        fy |= {(r[1], r[2]) for r in BCNF[rel][1]}
    BCNF['Fiscal_Year'] = (['Start_Year', 'End_Year'],
                           [list(x) for x in sorted(fy)])
    PK['Fiscal_Year'] = '(Start_Year, End_Year)'

    FK.update({
        'River_Station': ['River_Name -> River(River_Name)'],
        'Month_Time': ['Year -> Year_Time(Year)'],
        'Day_Time': ['(Year, Month) -> Month_Time(Year, Month)'],
        'Fiscal_Year': ['Start_Year -> Year_Time(Year)',
                        'End_Year -> Year_Time(Year)'],
        'Temperature_Record': ['Station_Name -> Station(Station_Name)',
                               '(Year, Month) -> Month_Time(Year, Month)'],
        'Humidity_Record': ['Station_Name -> Station(Station_Name)',
                            '(Year, Month) -> Month_Time(Year, Month)'],
        'Rainfall_Record': ['Station_Name -> Station(Station_Name)',
                            '(Year, Month) -> Month_Time(Year, Month)'],
        'Wind_Record': ['Station_Name -> Station(Station_Name)',
                        '(Year, Month) -> Month_Time(Year, Month)'],
        'Climatic_Event_Record': ['Station_Name -> Station(Station_Name)',
                                  '(Year, Month) -> Month_Time(Year, Month)'],
        'Sunshine_Record': ['Station_Name -> Station(Station_Name)',
                            '(Year, Month, Day) -> Day_Time(Year, Month, Day)'],
        'Radiation_Record': ['Station_Name -> Station(Station_Name)',
                             '(Year, Month, Day) -> Day_Time(Year, Month, Day)'],
        'Water_Quality': ['WQ_Station_Name -> River_Station(WQ_Station_Name)',
                          'Year -> Year_Time(Year)'],
        'Type_Of_Establishments': [
            'Size_Name -> Size(Size_Name)',
            '(Start_Year, End_Year) -> Fiscal_Year(Start_Year, End_Year)'],
        'Industry_Usage': [
            'Industry_Name -> Industrial_Type(Industry_Name)',
            '(Start_Year, End_Year) -> Fiscal_Year(Start_Year, End_Year)'],
        'Forest_Area_Record': [
            'District_Name -> District(District_Name)',
            '(Fiscal_Start_Year, Fiscal_End_Year) -> '
            'Fiscal_Year(Start_Year, End_Year)'],
    })


XFORM = {
    'bbs': 'Read from the Bangladesh Bureau of Statistics workbook. The '
           'repeating month columns are unpivoted into rows, the station is '
           'taken from the label row that stands above each group of data '
           'rows, and the published Annual column is discarded because it is '
           'the mean of the twelve months and would duplicate them.',
    'bmdt': 'Read from the Bangladesh Meteorological Department temperature '
            'workbook. One sheet holds one station, the year is a row and the '
            'twelve months are columns, so the columns are unpivoted into '
            'rows.',
    'bmds': 'Read from the Bangladesh Meteorological Department sunshine '
            'workbook. The thirty one day columns are unpivoted into rows and '
            'a day that does not exist in that month is rejected.',
    'brri': 'Read from a Bangladesh Rice Research Institute daily weather '
            'file and aggregated to the month, because the approved design '
            'holds monthly climate readings. Temperature and humidity are '
            'averaged over the days present, rainfall is summed, and the '
            'number of days each figure rests on is counted.',
    'gw': 'Read from the Bangladesh Water Development Board groundwater '
          'workbook. The district is named only on the first well of each '
          'group, so it is carried down to the wells that follow it.',
    'rivers': 'Read from the Bangladesh Water Development Board river '
              'register. One row per river, so no column group repeats.',
}

DERIVED_TRACE = [
    ('Station', 'Station_Name',
     'Collected from the station names used by the seven climate and daily '
     'relations, after name reconciliation.'),
    ('District', 'District_Name',
     'Collected from the district names used by Forest_Area_Record, after '
     'name reconciliation.'),
    ('River', 'River_Name',
     'The Bangladesh Water Development Board river register, plus the water '
     'bodies named by the water quality sheets that the register omits.'),
    ('Year_Time', 'Year',
     'Collected from every year used by any measurement relation.'),
    ('Month_Time', 'Year, Month',
     'Collected from every year and month pair used by any monthly relation.'),
    ('Day_Time', 'Year, Month, Day',
     'Collected from every year, month and day used by Sunshine_Record and '
     'Radiation_Record, after rejecting days that the month does not hold.'),
    ('Fiscal_Year', 'Start_Year, End_Year',
     'Split from the fiscal year text the forest sheet publishes, for example '
     '2019-20 becomes 2019 and 2020.'),
]


def build_trace():
    """Fill TRACE by measuring which block supplied each attribute.

    One row per relation and source block. The attribute list is measured, not
    declared: an attribute is listed only if that block actually supplied a
    non empty value for it, so a block that leaves a column empty throughout
    is not credited with it.
    """
    pairs = [(r, r + '_3NF') for r in
             ('Temperature_Record', 'Humidity_Record', 'Rainfall_Record',
              'Wind_Record', 'Climatic_Event_Record', 'Sunshine_Record',
              'Radiation_Record', 'Water_Quality')]
    loader = {b['id']: b['loader'] for b in BK.BLOCKS}
    rep = {b['id']: b['rep'] for b in BK.BLOCKS}

    def emit(rel, bid, attrs, nrows, extra=''):
        org, fil, sh = SRC_ORG[bid]
        TRACE.append((rel, ', '.join(attrs), org, fil, sh, rep[bid],
                      '%s It contributes %d rows to this relation before the '
                      'primary key is enforced.%s'
                      % (XFORM.get(loader[bid], ''), nrows, extra)))

    for rel, t3 in pairs:
        if t3 not in THREE_NF:
            continue
        hdr, rows = THREE_NF[t3]
        bcol = hdr.index('Block')
        per = {}
        for r in rows:
            e = per.setdefault(r[bcol], [0, set()])
            e[0] += 1
            for j, a in enumerate(hdr):
                if a != 'Block' and j < len(r) and r[j] is not None \
                        and r[j] != '':
                    e[1].add(a)
        for bid in sorted(per):
            n, attrs = per[bid]
            emit(rel, bid, [a for a in hdr if a in attrs], n)

    fhdr = THREE_NF['Forest_Area_Record_3NF'][0]
    per = {}
    for dn, fs, fe, measure, acre, bid in TWO_NF['Forest_Area_2NF'][1]:
        e = per.setdefault(bid, [set(), set()])
        e[0].add((dn, fs, fe))
        if acre is not None and acre != '':
            e[1].add(measure)
    for bid in sorted(per):
        keys, attrs = per[bid]
        emit('Forest_Area_Record', bid,
             [a for a in fhdr if a in attrs or a in
              ('District_Name', 'Fiscal_Start_Year', 'Fiscal_End_Year')],
             len(keys),
             ' The eight area figures are separate columns in the source, so '
             'the measure column that First Normal Form created is pivoted '
             'back into one row per district and fiscal year.')


    for b in BK.BLOCKS:
        if not b['target'].startswith(('Industrial_Type',
                                       'Type_Of_Establishments')):
            continue
        usage = b['target'].startswith('Industrial')
        rel = 'Industry_Usage' if usage else 'Type_Of_Establishments'
        key = 'Industry_Name' if usage else 'Size_Name'
        note = ('Read from the Bangladesh Bureau of Statistics workbook. The '
                'sheet publishes three fiscal years side by side, so the '
                'three year columns are unpivoted into three rows for each %s '
                'rather than reduced to the latest year. '
                % key.replace('_', ' ').lower())
        if usage:
            note += ('The produced and reused values are preserved in '
                     'separate columns; the source heading conflict is '
                     'documented rather than silently corrected.')
        else:
            note += ('The published quantity and percentage are preserved '
                     'as separate columns.')
        attrs = ('%s, Start_Year, End_Year, Produced_Waste_Water, '
                 'Reused_Waste_Water' % key if usage else
                 '%s, Start_Year, End_Year, Quantity, Percentage' % key)
        TRACE.append((rel, attrs, b['org'], b['file'], b['sheet'].strip(),
                      b['rep'], note))
        TRACE.append(('Industrial_Type' if usage else 'Size', key, b['org'],
                      b['file'], b['sheet'].strip(), b['rep'],
                      'A reference relation collected from the %s values that '
                      '%s actually uses, so the foreign key has a parent row.'
                      % (key.replace('_', ' ').lower(), rel)))

    riv = next((b for b in BK.BLOCKS if b['loader'] == 'rivers'), None)
    for rel, attr, note in DERIVED_TRACE:
        if rel == 'River' and riv is not None:
            TRACE.append((rel, attr, riv['org'], riv['file'],
                          riv['sheet'].strip(), riv['rep'], note))
        else:
            TRACE.append((rel, attr, 'derived', 'not published as a table',
                          '', 'no source column', note))
    TRACE.append(('River_Station', 'WQ_Station_Name, River_Name', 'BBS',
                  'BBS_Time_Series_Environmental_Database.xlsx',
                  'T1.84, T1.85',
                  'station column and river or lake heading',
                  'The monitoring point and the water body it stands in are '
                  'read from the water quality sheets. A marine point stands '
                  'in the sea, so the water body is recorded as Bay of '
                  'Bengal.'))


def stage_note(stage):
    return {
        '1NF': 'First Normal Form. Every repeating column group in the source '
               'is unpivoted into rows, so each cell holds one value. The '
               'tables are still wide and still carry provenance and measure '
               'columns, which is deliberate: those partial dependencies are '
               'what the Second Normal Form stage removes.',
        '2NF': 'Second Normal Form. Every non key attribute now depends on '
               'the whole candidate key. Attributes that depended on only '
               'part of the key were lifted into their own tables.',
        '3NF': 'Third Normal Form. No non key attribute depends on another '
               'non key attribute. Each measured quantity now has its own '
               'table, which is what the approved Entity Relationship '
               'diagram draws.',
        'BCNF': 'Boyce Codd Normal Form. Every determinant is a candidate '
                'key. The primary key of each relation is enforced here, so '
                'duplicate keys are resolved and the loss is recorded.',
    }[stage]


def write_stage(stage, tables):
    for name in sorted(tables):
        hdr, rows = tables[name]
        n, w = write_csv(stage, name, hdr, rows, cap=None)
        ROWCOUNT[(stage, name)] = n


def write_statistics():
    L = []
    L.append('# Load Statistics')
    L.append('')
    L.append('Every figure below is counted by the extraction program while '
             'it reads the source files. No figure is estimated.')
    L.append('')
    L.append('## 1. How much each source organisation contributes')
    L.append('')
    L.append('Two different figures are given, because they answer two '
             'different questions. The first counts values read out of the '
             'published files. The second counts rows that survive into the '
             'final database. They differ for one stated reason: the '
             'Bangladesh Rice Research Institute publishes a reading for '
             'every day, and the approved design records climate at month '
             'grain, so many daily readings become one row.')
    L.append('')
    per = collections.Counter()
    for b, c in CELLS_KEPT.items():
        per[SRC_ORG.get(b, ('?',))[0]] += c
    final = collections.Counter()
    for stage_rel, blockcol in (('Temperature_Record_3NF', -1),
                                ('Humidity_Record_3NF', -1),
                                ('Rainfall_Record_3NF', -1),
                                ('Wind_Record_3NF', -1),
                                ('Climatic_Event_Record_3NF', -1),
                                ('Sunshine_Record_3NF', -1),
                                ('Radiation_Record_3NF', -1),
                                ('Water_Quality_3NF', -1)):
        for r in THREE_NF[stage_rel][1]:
            final[SRC_ORG.get(r[blockcol], ('?',))[0]] += 1
    for r in THREE_NF['Forest_Area_Record_3NF'][1]:
        final['BBS'] += 1
    for r in THREE_NF['River_Register_3NF'][1]:
        final['BWDB'] += 1
    L.append('| Organisation | Raw blocks read | Values read from the source | '
             'Rows offered to the final database |')
    L.append('|---|---|---|---|')
    blk = collections.Counter(SRC_ORG[b][0] for b in SRC_ORG)
    for org in sorted(per, key=lambda o: -per[o]):
        L.append('| %s | %d | %d | %d |'
                 % (org, blk[org], per[org], final.get(org, 0)))
    L.append('| **Total** | **%d** | **%d** | **%d** |'
             % (len(SRC_ORG), sum(per.values()), sum(final.values())))
    L.append('')
    L.append('## 2. Cells read, kept and missing, per raw block')
    L.append('')
    L.append('| Block | Organisation | Sheet | Cells read | Values kept | '
             'Missing or unusable |')
    L.append('|---|---|---|---|---|---|')
    for b in sorted(CELLS_READ, key=lambda x: (x[0], int(x[1:]) if
                                               x[1:].isdigit() else 0)):
        o, f, s = SRC_ORG.get(b, ('?', '?', '?'))
        L.append('| %s | %s | %s | %d | %d | %d |'
                 % (b, o, s, CELLS_READ[b], CELLS_KEPT[b], MISSING[b]))
    L.append('| **Total** | | | **%d** | **%d** | **%d** |'
             % (sum(CELLS_READ.values()), sum(CELLS_KEPT.values()),
                sum(MISSING.values())))
    L.append('')
    L.append('## 3. Row counts through the normalization chain')
    L.append('')
    L.append('| Stage | Table | Rows |')
    L.append('|---|---|---|')
    for stage in ('1NF', '2NF', '3NF', 'BCNF'):
        for (st, nm), n in sorted(ROWCOUNT.items()):
            if st == stage:
                L.append('| %s | %s | %d |' % (st, nm, n))
    L.append('')
    L.append('## 4. Final relation sizes')
    L.append('')
    L.append('| Relation | Primary key | Attributes | Rows |')
    L.append('|---|---|---|---|')
    tot = 0
    for nm in sorted(BCNF):
        hdr, rows = BCNF[nm]
        tot += len(rows)
        L.append('| %s | %s | %d | %d |'
                 % (nm, PK.get(nm, ''), len(hdr), len(rows)))
    L.append('| **Total** | | | **%d** |' % tot)
    L.append('')
    L.append('## 5. Distinct key values in the loaded database')
    L.append('')
    L.append('| Reference set | Distinct values |')
    L.append('|---|---|')
    for nm in ('Station', 'District', 'River', 'River_Station', 'Year_Time',
               'Month_Time', 'Day_Time', 'Fiscal_Year'):
        L.append('| %s | %d |' % (nm, len(BCNF[nm][1])))
    L.append('')
    yrs = [r[0] for r in BCNF['Year_Time'][1]]
    if yrs:
        L.append('The loaded database covers the years %s to %s.'
                 % (min(yrs), max(yrs)))
    with open(OUT + 'STATISTICS.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


def write_quality():
    L = []
    L.append('# Data Quality Log')
    L.append('')
    L.append('Every problem the extraction program meets in the source files '
             'is counted here. Nothing is silently corrected: a repair is '
             'recorded as a repair, and a value that cannot be repaired is '
             'left empty rather than replaced with a zero.')
    L.append('')
    L.append('## 1. Problems found, by class')
    L.append('')
    L.append('| Problem found in the source | Times | Examples |')
    L.append('|---|---|---|')
    for k in sorted(ANOM, key=lambda x: -ANOM[x]):
        ex = '; '.join(ANOM_SAMPLE.get(k, []))[:220].replace('|', '/')
        L.append('| %s | %d | %s |' % (k.replace('|', '/'), ANOM[k], ex))
    L.append('')
    L.append('Total problem occurrences recorded: **%d** across **%d** '
             'distinct classes.' % (sum(ANOM.values()), len(ANOM)))
    L.append('')
    L.append('## 2. Station names reconciled')
    L.append('')
    L.append('The same weather station is spelled differently by different '
             'organisations, and sometimes differently within one file. Each '
             'variant is mapped to one canonical name so that the primary key '
             'of every climate relation is stable.')
    L.append('')
    L.append('| Name as published | Canonical name used |')
    L.append('|---|---|')
    for k in sorted(STATION_MAP_LOG):
        L.append('| %s | %s |' % (k, STATION_MAP_LOG[k]))
    L.append('')
    L.append('## 3. District names reconciled')
    L.append('')
    if DISTRICT_MAP_LOG:
        L.append('| Name as published | Canonical name used |')
        L.append('|---|---|')
        for k in sorted(DISTRICT_MAP_LOG):
            L.append('| %s | %s |' % (k, DISTRICT_MAP_LOG[k]))
    else:
        L.append('No district name needed correction.')
    L.append('')
    L.append('## 4. River names reconciled against the BWDB register')
    L.append('')
    if RIVER_MAP_LOG:
        L.append('| Name as published by BBS | Name in the BWDB register |')
        L.append('|---|---|')
        for k in sorted(RIVER_MAP_LOG):
            L.append('| %s | %s |' % (k, RIVER_MAP_LOG[k]))
    else:
        L.append('No river name needed mapping.')
    L.append('')
    L.append('## 5. Text found in a station column and dropped')
    L.append('')
    if STATION_DROPPED:
        L.append('| Value found | Times |')
        L.append('|---|---|')
        for k in sorted(STATION_DROPPED, key=lambda x: -STATION_DROPPED[x]):
            L.append('| %s | %d |' % (k.replace('|', '/'),
                                      STATION_DROPPED[k]))
    else:
        L.append('None.')
    L.append('')
    L.append('## 6. Primary key conflicts between organisations')
    L.append('')
    L.append('Where two organisations publish a different value for the same '
             'primary key, the key forbids both. The value from the '
             'higher precedence source is kept and the rejected value is '
             'recorded here, because a discarded measurement must remain '
             'visible.')
    L.append('')
    L.append('Precedence used: %s.'
             % ', '.join('%s before %s' % (a, b) for a, b in
                         [('Bangladesh Bureau of Statistics', 'Bangladesh '
                           'Meteorological Department'),
                          ('Bangladesh Meteorological Department',
                           'Bangladesh Rice Research Institute')]))
    L.append('')
    if CONFLICTS:
        L.append('### 6.1 Summary, and why the two kinds of conflict are '
                 'separated')
        L.append('')
        L.append('Most conflicts are the two organisations rounding the same '
                 'reading to a different number of decimal places. A '
                 'conflict is classed as rounding when the two figures agree '
                 'to within the tolerance stated for the relation, and as '
                 'substantive otherwise. Only the substantive conflicts mean '
                 'the two organisations disagree about what was measured.')
        L.append('')
        L.append('| Relation | Tolerance treated as rounding | Precedence '
                 'applied | Rounding | Substantive | Total |')
        L.append('|---|---|---|---|---|---|')
        pairs = sorted({(r, p) for r, p, _ in CONFLICT_CLASS})
        for rel, pair in pairs:
            ro = CONFLICT_CLASS.get((rel, pair, 'rounding'), 0)
            su = CONFLICT_CLASS.get((rel, pair, 'substantive'), 0)
            tol = ROUNDING_TOLERANCE.get(rel)
            L.append('| %s | %s | %s | %d | %d | %d |'
                     % (rel, ('%g' % tol) if tol is not None else 'none',
                        pair, ro, su, ro + su))
        tr = sum(v for (_, _, c), v in CONFLICT_CLASS.items()
                 if c == 'rounding')
        ts = sum(v for (_, _, c), v in CONFLICT_CLASS.items()
                 if c == 'substantive')
        L.append('| **Total** | | | **%d** | **%d** | **%d** |'
                 % (tr, ts, tr + ts))
        L.append('')
        L.append('### 6.2 Substantive conflicts')
        L.append('')
        sub = [c for c in CONFLICTS if c[6] == 'substantive']
        L.append('There are **%d** substantive conflicts. The largest are '
                 'listed below.' % len(sub))
        L.append('')

        def gap(c):
            try:
                a = [float(x) for x in c[3].split(', ') if x != '']
                b = [float(x) for x in c[5].split(', ') if x != '']
                return max(abs(x - y) for x, y in zip(a, b))
            except (ValueError, TypeError):
                return -1.0

        sub.sort(key=gap, reverse=True)
        L.append('| Relation | Key | Source kept | Value kept | Source '
                 'rejected | Value rejected | Difference |')
        L.append('|---|---|---|---|---|---|---|')
        for c in sub[:80]:
            g = gap(c)
            L.append('| %s | %s | %s | %s | %s | %s | %s |'
                     % (c[0], c[1], c[2], c[3], c[4], c[5],
                        ('%.2f' % g) if g >= 0 else 'not comparable'))
        L.append('')
        L.append('The complete list of all **%d** conflicts, rounding and '
                 'substantive together, is in '
                 '`csv/BCNF/_Key_Conflicts.csv`.' % len(CONFLICTS))
    else:
        L.append('No conflicting values were found.')
    L.append('')
    L.append('## 7. Identical duplicates removed')
    L.append('')
    L.append('These are rows where two sources publish the same value for the '
             'same key. Nothing is lost when the duplicate is dropped.')
    L.append('')
    if DUP_IDENTICAL:
        L.append('| Relation | Identical duplicate rows dropped |')
        L.append('|---|---|')
        for k in sorted(DUP_IDENTICAL, key=lambda x: -DUP_IDENTICAL[x]):
            L.append('| %s | %d |' % (k, DUP_IDENTICAL[k]))
    else:
        L.append('None.')
    L.append('')
    L.append('## 8. Raw blocks that could not be loaded at all')
    L.append('')
    if DROPPED_BLOCK:
        L.append('| Block | Source | Rows in the block | Reason it cannot be '
                 'loaded |')
        L.append('|---|---|---|---|')
        for b in sorted(DROPPED_BLOCK):
            lab, n, why = DROPPED_BLOCK[b]
            L.append('| %s | %s | %d | %s |' % (b, lab, n, why))
    else:
        L.append('None.')
    L.append('')
    L.append('## 9. Constraint verification on the loaded database')
    L.append('')
    L.append('The two constraints that a relational database enforces are '
             'checked against the loaded tables. Both are reported here as '
             'measured results, not as assertions.')
    L.append('')
    L.append('| Constraint checked | Relations checked | Violations found |')
    L.append('|---|---|---|')
    L.append('| Primary key holds no duplicate value | %d | %d |'
             % (VERIFY['pk_checked'], VERIFY['pk_violations']))
    L.append('| Every foreign key value exists in the parent relation | %d | '
             '%d |' % (VERIFY['fk_checked'], VERIFY['fk_violations']))
    L.append('')
    if VERIFY['detail']:
        L.append('Violations found:')
        L.append('')
        for d in VERIFY['detail']:
            L.append('- %s' % d)
    else:
        L.append('No violation of any kind is found. Every relation loads '
                 'with a unique primary key, and every foreign key value has '
                 'a matching parent row.')
    with open(OUT + 'DATA_QUALITY_LOG.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


VERIFY = {'pk_checked': 0, 'pk_violations': 0, 'fk_checked': 0,
          'fk_violations': 0, 'detail': []}

PK_COLS = {
    'Station': ['Station_Name'],
    'District': ['District_Name'],
    'River': ['River_Name'],
    'River_Station': ['WQ_Station_Name'],
    'Year_Time': ['Year'],
    'Month_Time': ['Year', 'Month'],
    'Day_Time': ['Year', 'Month', 'Day'],
    'Fiscal_Year': ['Start_Year', 'End_Year'],
    'Temperature_Record': ['Station_Name', 'Year', 'Month', 'Type'],
    'Humidity_Record': ['Station_Name', 'Year', 'Month'],
    'Rainfall_Record': ['Station_Name', 'Year', 'Month'],
    'Wind_Record': ['Station_Name', 'Year', 'Month', 'Type'],
    'Climatic_Event_Record': ['Station_Name', 'Year', 'Month'],
    'Sunshine_Record': ['Station_Name', 'Year', 'Month', 'Day'],
    'Radiation_Record': ['Station_Name', 'Year', 'Month', 'Day', 'Sample_No'],
    'Water_Quality': ['WQ_Station_Name', 'Year', 'Parameter_Type'],
    'Size': ['Size_Name'],
    'Industrial_Type': ['Industry_Name'],
    'Type_Of_Establishments': ['Size_Name', 'Start_Year', 'End_Year'],
    'Industry_Usage': ['Industry_Name', 'Start_Year', 'End_Year'],
    'Forest_Area_Record': ['District_Name', 'Fiscal_Start_Year',
                           'Fiscal_End_Year'],
}

FK_PAIRS = [
    ('River_Station', ['River_Name'], 'River', ['River_Name']),
    ('Month_Time', ['Year'], 'Year_Time', ['Year']),
    ('Day_Time', ['Year', 'Month'], 'Month_Time', ['Year', 'Month']),
    ('Fiscal_Year', ['Start_Year'], 'Year_Time', ['Year']),
    ('Fiscal_Year', ['End_Year'], 'Year_Time', ['Year']),
    ('Water_Quality', ['WQ_Station_Name'], 'River_Station',
     ['WQ_Station_Name']),
    ('Water_Quality', ['Year'], 'Year_Time', ['Year']),
    ('Type_Of_Establishments', ['Size_Name'], 'Size', ['Size_Name']),
    ('Type_Of_Establishments', ['Start_Year', 'End_Year'], 'Fiscal_Year',
     ['Start_Year', 'End_Year']),
    ('Industry_Usage', ['Industry_Name'], 'Industrial_Type',
     ['Industry_Name']),
    ('Industry_Usage', ['Start_Year', 'End_Year'], 'Fiscal_Year',
     ['Start_Year', 'End_Year']),
    ('Forest_Area_Record', ['District_Name'], 'District', ['District_Name']),
    ('Forest_Area_Record', ['Fiscal_Start_Year', 'Fiscal_End_Year'],
     'Fiscal_Year', ['Start_Year', 'End_Year']),
] + [(r, ['Station_Name'], 'Station', ['Station_Name']) for r in
     ('Temperature_Record', 'Humidity_Record', 'Rainfall_Record',
      'Wind_Record', 'Climatic_Event_Record', 'Sunshine_Record',
      'Radiation_Record')
     ] + [(r, ['Year', 'Month'], 'Month_Time', ['Year', 'Month']) for r in
          ('Temperature_Record', 'Humidity_Record', 'Rainfall_Record',
           'Wind_Record', 'Climatic_Event_Record')
          ] + [(r, ['Year', 'Month', 'Day'], 'Day_Time',
                ['Year', 'Month', 'Day']) for r in
               ('Sunshine_Record', 'Radiation_Record')]


def verify():
    def proj(rel, cols):
        hdr, rows = BCNF[rel]
        idx = [hdr.index(c) for c in cols]
        return [tuple(r[i] for i in idx) for r in rows]

    for rel, cols in PK_COLS.items():
        VERIFY['pk_checked'] += 1
        k = proj(rel, cols)
        if len(k) != len(set(k)):
            VERIFY['pk_violations'] += 1
            VERIFY['detail'].append(
                'Primary key of %s repeats %d times.'
                % (rel, len(k) - len(set(k))))
    for child, ccols, parent, pcols in FK_PAIRS:
        VERIFY['fk_checked'] += 1
        miss = set(proj(child, ccols)) - set(proj(parent, pcols))
        if miss:
            VERIFY['fk_violations'] += 1
            VERIFY['detail'].append(
                '%s.%s has %d value(s) absent from %s, for example %s.'
                % (child, ', '.join(ccols), len(miss), parent,
                   sorted(str(m) for m in miss)[:3]))
    return VERIFY['pk_violations'] + VERIFY['fk_violations']


FD_ROWS = [
    ('Station', 'Station_Name', 'Station_Name', 'the key alone', 'yes',
     'The relation holds only its key, so there is nothing to violate.'),
    ('District', 'District_Name', 'District_Name', 'the key alone', 'yes',
     'The relation holds only its key.'),
    ('River', 'River_Name', 'River_Name', 'the key alone', 'yes',
     'The relation holds only its key.'),
    ('River_Station', 'WQ_Station_Name',
     'WQ_Station_Name -> River_Name', 'the whole key', 'yes',
     'The approved diagram identifies each monitoring point by its water '
     'quality station name. All 323 loaded names are distinct.'),
    ('Year_Time', 'Year', 'Year', 'the key alone', 'yes',
     'A calendar year that at least one measurement uses.'),
    ('Month_Time', '(Year, Month)', '(Year, Month)', 'the key alone', 'yes',
     'A year and month pair that at least one measurement uses.'),
    ('Day_Time', '(Year, Month, Day)', '(Year, Month, Day)',
     'the key alone', 'yes',
     'A calendar date. The foreign key to Month_Time is composite, because '
     'two single column foreign keys would not force the year and month to '
     'occur together as a valid pair.'),
    ('Fiscal_Year', '(Start_Year, End_Year)', '(Start_Year, End_Year)',
     'the key alone', 'yes',
     'Forest statistics report on a July to June fiscal year, so both '
     'endpoints are stored and the span is explicit.'),
    ('Temperature_Record', '(Station_Name, Year, Month, Type)',
     '(Station_Name, Year, Month, Type) -> Temp', 'the whole key', 'yes',
     'Type separates the monthly maximum from the monthly minimum, so it is '
     'part of the key rather than a non key attribute.'),
    ('Humidity_Record', '(Station_Name, Year, Month)',
     '(Station_Name, Year, Month) -> Humidity', 'the whole key', 'yes',
     'One relative humidity figure for one station in one month.'),
    ('Rainfall_Record', '(Station_Name, Year, Month)',
     '(Station_Name, Year, Month) -> Rainfall', 'the whole key', 'yes',
     'One rainfall total for one station in one month.'),
    ('Wind_Record', '(Station_Name, Year, Month, Type)',
     '(Station_Name, Year, Month, Type) -> Wind_Speed, Direction',
     'the whole key', 'yes',
     'Speed and direction are recorded as one reading in the source, so both '
     'are non key attributes of the same functional dependency.'),
    ('Climatic_Event_Record', '(Station_Name, Year, Month)',
     '(Station_Name, Year, Month) -> Thunderstorm, Lightning',
     'the whole key', 'yes',
     'Both attributes count days in the same month at the same station, so '
     'they share one key and belong in one relation.'),
    ('Sunshine_Record', '(Station_Name, Year, Month, Day)',
     '(Station_Name, Year, Month, Day) -> Sunshine_Hours', 'the whole key',
     'yes', 'Bright sunshine hours for one station on one day.'),
    ('Radiation_Record', '(Station_Name, Year, Month, Day, Sample_No)',
     '(Station_Name, Year, Month, Day, Sample_No) -> Radiation',
     'the whole key', 'yes',
     'Sample_No is the hour of observation. The source sheet labels that '
     'column Date, which is a mislabel: the values run 0, 1, 2, 3 while the '
     'radiation figures rise from 0.0 through 0.2, 0.8 and 2.0, which is the '
     'sun rising during one day and not a change of date.'),
    ('Water_Quality', '(WQ_Station_Name, Year, Parameter_Type)',
     '(WQ_Station_Name, Year, Parameter_Type) -> Value', 'the whole key',
     'yes',
     'Parameter_Type names the measured quantity, and one station reports '
     'several parameters in the same year, so it is part of the key.'),
    ('Size', 'Size_Name', 'none beyond the key', 'the whole key', 'yes',
     'A reference relation naming the four enterprise sizes: Micro, Small, '
     'Medium and Large.'),
    ('Industrial_Type', 'Industry_Name', 'none beyond the key',
     'the whole key', 'yes',
     'A reference relation naming the industry categories that report reused '
     'waste water.'),
    ('Type_Of_Establishments', '(Size_Name, Start_Year, End_Year)',
     '(Size_Name, Start_Year, End_Year) -> Quantity, Percentage',
     'the whole key', 'yes',
     'The fiscal year belongs in the key because the source publishes three '
     'years side by side for each of the four sizes. Percentage is Quantity '
     'measured against the column total for its own year, so it is derivable. '
     'It is kept because the approved diagram carries it and the source '
     'publishes it as a separate figure.'),
    ('Industry_Usage', '(Industry_Name, Start_Year, End_Year)',
     '(Industry_Name, Start_Year, End_Year) -> Produced_Waste_Water, '
     'Reused_Waste_Water',
     'the whole key', 'yes',
     'Both published waste-water values belong to one industry and fiscal '
     'year. The reuse rate is calculated from them in a database view rather '
     'than stored as a misleading source percentage.'),
    ('Forest_Area_Record',
     '(District_Name, Fiscal_Start_Year, Fiscal_End_Year)',
     'the whole key determines all eight area figures', 'the whole key',
     'yes',
     'The two totals are sums of the component areas, so they are derivable. '
     'They are kept because a stored total lets a load time check catch an '
     'extraction error, and the source contains one: district Gazipur is '
     'published as 65.173.21 where the computed total is 65173.21.'),
]


def main():
    build_source_index()
    print('Reading selected source files.')
    raw_inventory = BK.emit_0nf()
    print('  raw blocks    : %d' % len(raw_inventory))
    run_parsers()
    print('  climate rows  : temp %d  hum %d  rain %d  wind %d  event %d'
          % (len(TEMP), len(HUM), len(RAIN), len(WIND), len(EVENT)))
    print('  daily rows    : sun %d  rad %d' % (len(SUN), len(RAD)))
    print('  water quality : %d   ground water : %d' % (len(WQ), len(GW)))
    print('  forest %d  industry %d  establishment %d  rivers %d'
          % (len(FOREST), len(IND), len(EST), len(RIVREG)))
    build_1nf()
    build_2nf()
    build_3nf()
    build_bcnf()
    build_trace()
    bad = verify()
    print('Checking normalized relations.')
    print('  primary keys : %d relations, %d violations'
          % (VERIFY['pk_checked'], VERIFY['pk_violations']))
    print('  foreign keys : %d references, %d violations'
          % (VERIFY['fk_checked'], VERIFY['fk_violations']))
    for d in VERIFY['detail']:
        print('  ! %s' % d)
    print('Writing normalization files.')
    write_stage('1NF', ONE_NF)
    write_stage('2NF', TWO_NF)
    write_stage('3NF', THREE_NF)
    write_stage('BCNF', BCNF)
    write_csv('BCNF', '_Key_Conflicts',
              ['Relation', 'Primary_Key', 'Source_Kept', 'Value_Kept',
               'Source_Rejected', 'Value_Rejected', 'Conflict_Class'],
              [list(c) for c in CONFLICTS])
    write_csv('BCNF', '_Functional_Dependencies',
              ['Relation', 'Candidate_Keys', 'Functional_Dependency',
               'Determinant', 'Determinant_Is_A_Candidate_Key', 'Explanation'],
              [list(r) for r in FD_ROWS])
    write_csv('BCNF', '_Traceability',
              ['Relation', 'Attribute', 'Organisation', 'Source_File',
               'Source_Sheet', 'Source_Column_Group', 'Transformation'],
              [list(r) for r in TRACE])
    write_statistics()
    write_quality()
    print('Normalization files refreshed.')
    for stage in ('1NF', '2NF', '3NF', 'BCNF'):
        tot = sum(n for (s, _), n in ROWCOUNT.items() if s == stage)
        print('  %-5s %2d tables %8d rows'
              % (stage, sum(1 for (s, _) in ROWCOUNT if s == stage), tot))


if __name__ == '__main__':
    main()
