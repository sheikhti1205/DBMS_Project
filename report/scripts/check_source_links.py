"""Record anonymous access checks for retained Drive file links (not publisher URLs)."""
import concurrent.futures
import datetime as dt
import html
import json
from pathlib import Path
import re
import urllib.request

HERE = Path(__file__).resolve().parent

def check(item):
    name, entry = item
    url = entry.get('url') or 'https://drive.google.com/file/d/' + entry['id'] + '/view'
    record = {'file': name, 'url': url, 'checked_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=40) as response:
            body = response.read(2_000_000).decode('utf-8', 'replace')
            match = re.search(r'<title>(.*?)</title>', body, re.S)
            title = html.unescape(match.group(1)) if match else ''
            record.update(http_status=response.status, title=title,
                          accessible=response.status == 200 and name in title and 'accounts.google.com' not in response.url)
    except Exception as exc:
        record.update(accessible=False, error=str(exc))
    return record

def main():
    mapping = json.loads((HERE / 'drive_file_map.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(check, sorted(mapping.items())))
    output = {'scope': 'Anonymous retained-copy preview access, with matching filename in page title. Not a publisher-site access log or full-content validation.', 'files': records,
              'supporting_links': [check(item) for item in [
                  ('Selected_Source_Files', {'url': 'https://drive.google.com/drive/folders/1SSdmo-VFQ6leS7Gp8hItmksg_SxRMl3q'}),
                  ('Team-7_BD_Environment_Data_Resources.xlsx', {'id': '1UB5vrVxfrtvFXZUDgvV4bsBDaMcvC2sw'}),
              ]]}
    (HERE / 'source_access_checks.json').write_text(json.dumps(output, indent=2) + '\n')
    print(f"Accessible: {sum(r['accessible'] for r in records)}/{len(records)}")
    failures = [record for record in records + output["supporting_links"]
                if not record["accessible"]]
    for record in failures:
        print(record)
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
