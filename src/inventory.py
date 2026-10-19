"""Inventory review using purely fabricated asset observations."""
import argparse
import csv
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path


def load_table(path, fields):
    with Path(path).open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(fields).issubset(reader.fieldnames):
            raise ValueError(f'Expected CSV columns: {", ".join(fields)}')
        rows = []
        for line, row in enumerate(reader, 2):
            item = {k: (row.get(k) or '').strip() for k in fields}
            if any(not v for v in item.values()):
                raise ValueError(f'Line {line}: missing data')
            rows.append(item)
        return rows


def classify_assets(assets, observations, as_of, window_days=21):
    """Return dashboard rows. Unknown is not a synonym for lost."""
    as_of = date.fromisoformat(str(as_of))
    ids = [x['asset_id'] for x in assets]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate asset identifiers')
    history = {id_: [] for id_ in ids}
    for obs in observations:
        if obs['asset_id'] not in history:
            raise ValueError(f'Observation references an unknown asset: {obs["asset_id"]}')
        observed = date.fromisoformat(obs['observed_on'])
        if observed > as_of:
            raise ValueError('Observation occurs after reference date')
        if obs['result'] not in {'Pass', 'Review'}:
            raise ValueError('Unknown observation result')
        history[obs['asset_id']].append((observed, obs['result']))
    output = []
    for asset in assets:
        if asset['state'] not in {'Active', 'Archived'}:
            raise ValueError('Unknown asset lifecycle state')
        observations_for_asset = sorted(history[asset['asset_id']])
        last_seen = observations_for_asset[-1] if observations_for_asset else None
        if asset['state'] == 'Archived':
            label = 'Archived'
        elif not last_seen:
            label = 'Unknown'
        elif last_seen[1] == 'Review':
            label = 'Review'
        elif (as_of - last_seen[0]).days > window_days:
            label = 'Outdated'
        else:
            label = 'Verified'
        output.append({**asset, 'status': label, 'last_observation': last_seen[0].isoformat() if last_seen else '—'})
    return sorted(output, key=lambda r: (r['status'], r['asset_id']))


def dashboard(rows, as_of):
    totals = Counter(r['status'] for r in rows)
    order = ('Verified', 'Review', 'Outdated', 'Unknown', 'Archived')
    kpis = ''.join('<div class="metric"><small>' + escape(k) + '</small><strong>' + str(totals[k]) + '</strong></div>' for k in order)
    lines = []
    for r in rows:
        search = ' '.join(r.values()).lower()
        lines.append('<tr data-search="' + escape(search, quote=True) + '">' +
            '<td><b>' + escape(r['asset_id']) + '</b></td><td>' + escape(r['category']) + '</td><td>' + escape(r['custodian']) + '</td>' +
            '<td>' + escape(r['last_observation']) + '</td><td><span class="tag ' + r['status'].lower() + '">' + escape(r['status']) + '</span></td></tr>')
    return """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Asset Inventory Demo</title><style>body{font:15px system-ui,Arial;background:#f5f7fa;color:#1c2b3c;max-width:1080px;margin:28px auto;padding:0 16px}
header{display:flex;justify-content:space-between;align-items:center}.muted{color:#607186}.flag{font-size:12px;background:#e4ebf2;padding:8px;border-radius:30px}
.metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:9px;margin:22px 0}.metric{background:white;padding:13px;border:1px solid #dce3eb;border-radius:11px}
.metric small,.metric strong{display:block}.metric strong{font-size:24px;padding-top:6px}input{padding:11px;border:1px solid #bdc9d5;border-radius:8px;width:100%;box-sizing:border-box}
[hidden]{display:none!important}table{border-collapse:collapse;width:100%;background:white;margin-top:13px}th,td{padding:13px;text-align:left;border-bottom:1px solid #e1e8ef}th{background:#e9eef4}
.tag{padding:5px 9px;border-radius:20px;font-size:12px}.verified{background:#daf2e5;color:#215b42}.review{background:#ffe8c8;color:#7e4d06}
.outdated{background:#fbe8db;color:#8a4324}.unknown{background:#e8eaf4;color:#485879}.archived{background:#ebebeb;color:#666}
.note{margin:18px 0;font-size:12px;color:#637486}@media(max-width:740px){.metrics{grid-template-columns:repeat(2,1fr)}table{font-size:12px}th,td{padding:7px}}
</style></head><body><header><div><h1>Asset Inventory</h1><p class="muted">Reference date: """ + escape(str(as_of)) + """ · Invented records</p></div><span class="flag">SYNTHETIC DEMO</span></header>
<div class="metrics">""" + kpis + """</div><label>Filter assets <input id="filter" placeholder="Search identifier, category, custodian" aria-label="Filter assets"></label>
<table><thead><tr><th>Asset</th><th>Category</th><th>Custodian</th><th>Last observation</th><th>Assessment</th></tr></thead><tbody>""" + ''.join(lines) + """</tbody></table>
<p class="note">An unknown or outdated observation does not prove an asset is missing. Status logic is for this demo only.</p>
<script>document.getElementById('filter').addEventListener('input',e=>{let q=e.target.value.trim().toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.dataset.search.includes(q));});</script>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', default='sample_data/assets.csv', type=Path)
    parser.add_argument('--observations', default='sample_data/observations.csv', type=Path)
    parser.add_argument('--as-of', default='2026-10-18')
    parser.add_argument('--output', default='output/assets.html', type=Path)
    args = parser.parse_args()
    assets = load_table(args.assets, ('asset_id', 'category', 'custodian', 'state'))
    observations = load_table(args.observations, ('asset_id', 'observed_on', 'result'))
    rows = classify_assets(assets, observations, args.as_of)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dashboard(rows, args.as_of), encoding='utf-8')
    print(f'Created {args.output} from {len(rows)} synthetic assets')


if __name__ == '__main__':
    main()
