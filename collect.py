import csv
import json
import os
import pathlib
import random
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = 'https://push2his.eastmoney.com/api/qt/stock/trends2/get'
SYMBOLS = {'002463': '0.002463'}
ROOT = pathlib.Path(__file__).resolve().parent
TZ = ZoneInfo('Asia/Shanghai')


def fetch(secid):
    params = {'secid': secid, 'fields1': 'f1,f2,f3,f4,f5',
              'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
              'iscr': '0', 'ndays': '5'}
    url = BASE + '?' + urlencode(params)
    last_error = None
    for attempt in range(4):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://quote.eastmoney.com/', 'Accept': 'application/json'})
            with urlopen(req, timeout=25) as response:
                payload = json.load(response)
            data = payload.get('data')
            if not isinstance(data, dict) or not isinstance(data.get('trends'), list) or not data['trends']:
                raise ValueError(f'Empty or unexpected response: {str(payload)[:400]}')
            return payload
        except Exception as exc:
            last_error = exc
            print(f'Attempt {attempt + 1} failed: {exc}', file=sys.stderr)
            if attempt < 3:
                time.sleep(3 * (attempt + 1) + random.random())
    raise RuntimeError(f'All requests failed: {last_error}')


def process(symbol, payload):
    data = payload['data']
    rows_by_date = {}
    for line in data['trends']:
        parts = line.split(',')
        if len(parts) < 8:
            raise ValueError(f'Unexpected minute row: {line}')
        stamp = parts[0]
        date = stamp.split(' ')[0]
        if not (len(date) == 10 and date[4] == '-' and date[7] == '-'):
            raise ValueError(f'Invalid timestamp: {stamp}')
        rows_by_date.setdefault(date, []).append(parts)

    for date, rows in rows_by_date.items():
        folder = ROOT / 'data' / symbol / date
        folder.mkdir(parents=True, exist_ok=True)
        # Preserve original raw minute strings and metadata to allow schema re-interpretation.
        raw_path = folder / 'raw.json'
        raw_path.write_text(json.dumps({'source': 'eastmoney_trends2', 'secid': SYMBOLS[symbol],
                                        'date': date, 'response_metadata': {k: v for k, v in data.items() if k != 'trends'},
                                        'trends': [','.join(r) for r in rows]}, ensure_ascii=False, indent=2), encoding='utf-8')
        csv_path = folder / 'minutes.csv'
        with csv_path.open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(['timestamp', 'f52', 'f53', 'f54', 'f55', 'f56', 'f57', 'f58'])
            writer.writerows(rows)
        print(f'{symbol} {date}: {len(rows)} minute records saved')
        if len(rows) < 200:
            print(f'WARNING: {symbol} {date} only {len(rows)} records; verify suspension/partial day', file=sys.stderr)


def main():
    now = datetime.now(TZ)
    print(f'Collection started {now.isoformat()}')
    for symbol, secid in SYMBOLS.items():
        process(symbol, fetch(secid))


if __name__ == '__main__':
    main()
