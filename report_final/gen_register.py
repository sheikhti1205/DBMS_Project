#!/usr/bin/env python3
"""Generate the Source Discovery register tables for the final report.

  generated/used_source_files.tex          - the 9 pipeline-input files (table)
  generated/official_source_register.tex   - official collected files (longtable)
  generated/unofficial_source_register.tex - unofficial collected files (longtable)

Reads register_data.csv, the minimal committed register input: one row per
collected source or data file with its family (org), file name, type (ext),
author or creator, and recorded last access date.  Those dates follow the
verified 2-29 April 2026 discovery and verification schedule used throughout
the report; this script never uses a run-time date.  The official and unofficial
longtables together partition the 75 collected files exactly; the selected
table is the deliberate 9-file subset and may repeat those files.  Each printed
file name links to the actual file in the shared project Google Drive folder
using drive_file_map.json, which records the public Drive item id for every
registered file.  Rows are ordered by source, then file type (Excel, CSV, PDF,
others) and then file name; no size column is printed.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
META = os.path.join(HERE, "register_data.csv")
DRIVE = os.path.join(HERE, "drive_file_map.json")

# Publisher labels for the register families (all official under the report's
# classification rule).  'Other' is handled per file in OTHER below.
ORG_FULL = {"BBS": "Bangladesh Bureau of Statistics",
            "BMD": "Bangladesh Meteorological Department",
            "BRRI": "Bangladesh Rice Research Institute",
            "BWDB": "Bangladesh Water Development Board",
            "DoE": "Department of Environment",
            "MoEFCC": "Ministry of Environment, Forest and Climate Change",
            "HDX": "Humanitarian Data Exchange",
            "UN": "United Nations",
            "UNESCO": "UNESCO",
            "WHO": "World Health Organization",
            "WorldBank": "World Bank"}

# Evidence-based publisher and classification for files stored under the
# 'Other' register family.  True = official, False = unofficial.
OTHER = {
    "2021_Henry_Forest_Ecosys.pdf": ("Springer (Forest Ecosystems)", False),
    "EnergyData_Cyclonic_Storm_Landfalls_File_1.xlsx":
        ("World Bank (energydata.info)", True),
    "EnergyData_Dhaka_Operations_Report.pdf":
        ("World Bank (energydata.info)", True),
    "FAO_3148.pdf": ("FAO", True),
    "FAO_384b.pdf": ("FAO", True),
    "FAO_6086-f.pdf": ("FAO", True),
    "FAO_6087.pdf": ("FAO", True),
    "FAO_9001.pdf": ("FAO", True),
    "FAO_966.pdf": ("FAO", True),
    "FAO_BFI-Report_final_08_02_2021.pdf": ("FAO", True),
    "FAO_BFI_analysis_document_final_v4.pdf": ("FAO", True),
    "FAO_BFI_manual.pdf": ("FAO", True),
    "FAO_OpenKnowledge_Content.pdf": ("FAO", True),
    "FAO_OpenKnowledge_Content_repaired.pdf": ("FAO", True),
    "GLA_Data_Sarker_693.xlsx": ("University of Glasgow", False),
    "GLA_researchdata_eprint_693.csv": ("University of Glasgow", False),
    "GW_locations_metadata.csv": ("HydroShare (CUAHSI)", False),
    "monthly_groundwater_levels.xlsx": ("HydroShare (CUAHSI)", False),
    "VTechWorks_Bangladesh_Item_Download.pdf": ("Virginia Tech (VTechWorks)", False),
    "WDPA_WDOECM_May2026_Public_BGD_csv.csv": ("UNEP-WCMC (Protected Planet)", True),
}

# Display order of the publisher labels inside each register.
OFFICIAL_ORDER = ["Bangladesh Bureau of Statistics",
                  "Bangladesh Meteorological Department",
                  "Bangladesh Rice Research Institute",
                  "Bangladesh Water Development Board",
                  "Department of Environment",
                  "Ministry of Environment, Forest and Climate Change",
                  "Humanitarian Data Exchange",
                  "United Nations",
                  "UNESCO",
                  "World Health Organization",
                  "World Bank",
                  "World Bank (energydata.info)",
                  "FAO",
                  "UNEP-WCMC (Protected Planet)"]
UNOFFICIAL_ORDER = ["HydroShare (CUAHSI)",
                    "Springer (Forest Ecosystems)",
                    "University of Glasgow",
                    "Virginia Tech (VTechWorks)"]

# The 9 structured loader files (report source-inventory pipeline input)
PIPELINE = {
    "BBS_Time_Series_Environmental_Database.xlsx",
    "Temperature Data.pdf",
    "Sunshine.xls",
    "BRRI_Daily_Maximum_Temperature.xlsx",
    "BRRI_Daily_Minimum_Temperature.xlsx",
    "BRRI_Daily_Average_Humidity.xlsx",
    "BRRI_Daily_Sunshine.xlsx",
    "BRRI_Daily_Total_Rainfall.xlsx",
    "BWDB_Rivers_Information.csv",
}

# Meaningful account authors are kept; meaningless account names and empty
# values are reported as 'Not identified' (never an em dash).
AUTHOR_CLEAN = {
    "met1": "BMD (internal account)",
    "XEN-SWPB": "XEN-SWPB (BWDB)",
    "SWPB Server": "SWPB server (BWDB)",
    "Head_Stat": "Head of Statistics (BRRI)",
}

# Absolute row order of file types inside each source group: Excel workbooks
# first, then CSV, then PDF and any remaining type.
TYPE_ORDER = {"XLSX": 0, "XLS": 1, "CSV": 2, "PDF": 3}


def clean_author(a):
    a = (a or "").strip()
    if a in AUTHOR_CLEAN:
        return AUTHOR_CLEAN[a]
    if a.startswith("Matieu Henry"):
        return "Matieu Henry and others (FAO)"
    if a.startswith("Fabian"):
        return "Fabian En\\ss{}le (GAF AG)"
    if "World Heritage Centre" in a:
        return "UNESCO World Heritage Centre"
    if a == "FAO-NFI":
        return "FAO National Forest Inventory"
    if a == "Falgoonee Kumar":
        return "Falgoonee Kumar Mondal"
    if a == "Chakma, Nikhil (FAOBD)":
        return "Nikhil Chakma (FAO)"
    if a in ("Home", "IBM", "David", "User", "admin", "SK", "Microsoft Office User"):
        return "Not identified"
    return a or "Not identified"


def esc(s):
    return s.replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def link_cell(file_name, url):
    body = f"\\texttt{{\\seqsplit{{{esc(file_name)}}}}}"
    return f"\\href{{{url}}}{{{body}}}" if url else body


def type_rank(t):
    return TYPE_ORDER.get(t, len(TYPE_ORDER))


def load():
    rows = {}
    for r in csv.DictReader(open(META)):
        if r["is_source"] != "True":
            continue
        org = r["org"]
        if org in ("Govt_File_mapping.xlsx", "Non-Govt_File_mapping.xlsx",
                   "Govt", "Non-Govt", ""):
            continue
        if r["file"] == "script.ps1":
            continue
        rows[r["file"]] = r
    return rows


def publisher_of(r):
    org = r["org"]
    if org == "Other":
        if r["file"] not in OTHER:
            raise SystemExit(f"no classification for Other file: {r['file']}")
        return OTHER[r["file"]]
    if org not in ORG_FULL:
        raise SystemExit(f"unexpected register family: {org} ({r['file']})")
    return ORG_FULL[org], True


def rank(label, order):
    try:
        return order.index(label)
    except ValueError:
        return len(order)


def main():
    rows = load()
    with open(DRIVE) as f:
        drive_map = json.load(f)
    missing = [f for f in rows if f not in drive_map]
    if missing:
        raise SystemExit(f"no Drive file id for: {', '.join(missing)}")

    def drive_url(f):
        return ("https://drive.google.com/file/d/%s/view?usp=sharing"
                % drive_map[f]["id"])

    def rec(f):
        r = rows[f]
        label, official = publisher_of(r)
        date = r["last_access_date"].strip()
        if not date:
            raise SystemExit(f"missing last access date for {f}")
        return {"file": f, "org": r["org"], "label": label, "official": official,
                "type": r["ext"][1:].upper(), "author": clean_author(r["author"]),
                "date": date, "url": drive_url(f)}

    def sort_key(e):
        order = (OFFICIAL_ORDER if e["official"] else UNOFFICIAL_ORDER)
        return (rank(e["label"], order), type_rank(e["type"]), e["file"])

    used = sorted((rec(f) for f in PIPELINE), key=sort_key)
    full = [rec(f) for f in sorted(rows)]
    if len(full) != 75:
        raise SystemExit(f"expected 75 collected files, found {len(full)}")
    if len(used) != 9:
        raise SystemExit(f"expected 9 selected files, found {len(used)}")
    official = sorted((e for e in full if e["official"]), key=sort_key)
    unofficial = sorted((e for e in full if not e["official"]), key=sort_key)

    head = ("No. & Source & Source file & Type & Author / creator & "
            "Last Access Date \\\\")
    cols = "{c L{2.45cm} L{4.05cm} C{0.9cm} L{2.15cm} C{1.6cm}}"

    def tex_row(i, e):
        return (f"{i} & {esc(e['label'])} & {link_cell(e['file'], e['url'])} & "
                f"{esc(e['type'])} & {esc(e['author'])} & {e['date']} \\\\")

    with open(os.path.join(HERE, "generated", "used_source_files.tex"), "w") as w:
        w.write(r"""% Generated by gen_register.py; do not edit manually.
\begin{table}[H]
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.25}
\caption{Pipeline-input source files: the \mSourceFiles{} structured files selected for
processing. The BMD sunshine workbook is retained as pipeline input but its two sunshine
blocks cannot be loaded because the source provides no usable station identity. Each
printed file name links to the corresponding file in the shared project Drive folder.}
\label{tab:used-source-files}
\begin{tabular}""" + cols + r"""
\toprule
""" + head + r"""
\midrule
""")
        for i, e in enumerate(used, 1):
            w.write(tex_row(i, e) + "\n")
        w.write(r"""\bottomrule
\end{tabular}
\end{table}
""")

    def write_register(out, entries, caption, label):
        n = len(entries)
        with open(os.path.join(HERE, "generated", out), "w") as w:
            w.write(r"""% Generated by gen_register.py; do not edit manually.
\begingroup
\footnotesize
\setlength{\tabcolsep}{2.6pt}
\renewcommand{\arraystretch}{1.12}
\begin{longtable}""" + cols + "\n"
                + "\\caption{" + caption + "}\n"
                + "\\label{" + label + "}\\\\\n"
                + r"""\toprule
""" + head + "\n" + r"""\midrule
\endfirsthead
\multicolumn{6}{l}{\textbf{\tablename\ \thetable\ (continued)}}\\
\toprule
""" + head + "\n" + r"""\midrule
\endhead
\bottomrule
\multicolumn{6}{r}{\emph{continued on next page}}\\
\endfoot
\bottomrule
\endlastfoot
""")
            for i, e in enumerate(entries, 1):
                w.write(tex_row(i, e) + "\n")
            w.write(r"""\end{longtable}
\endgroup
""")
        return n

    n_off = write_register(
        "official_source_register.tex", official,
        "Official source file register (69 files). Source file names link to the "
        "corresponding file in the shared project Drive folder.",
        "tab:official-source-register")
    n_uno = write_register(
        "unofficial_source_register.tex", unofficial,
        "Unofficial source file register (6 files). Source file names link to the "
        "corresponding file in the shared project Drive folder.",
        "tab:unofficial-source-register")

    assert n_off + n_uno == len(full) == 75
    overlap = {e["file"] for e in official} & {e["file"] for e in unofficial}
    assert not overlap
    print(f"selected: {len(used)} | official: {n_off} | unofficial: {n_uno} | "
          f"total: {n_off + n_uno}")


if __name__ == "__main__":
    main()
