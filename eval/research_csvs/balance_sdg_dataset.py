import csv
import re
import requests
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

URL = 'https://app.digitalpublicgoods.net/api/v1/dpgs'
OUT_PATH = Path('tese_set_2.csv')
ALLOWED_REPO_HOSTS = {'github.com', 'gitlab.com', 'codeberg.org', 'bitbucket.org'}
TARGET_COUNT = {
    1: 10,
    2: 10,
    3: 10,
    4: 10,
    5: 10,
    6: 10,
    7: 7,
    8: 10,
    9: 10,
    10: 10,
    11: 10,
    12: 10,
    13: 10,
    14: 7,
    15: 10,
    16: 10,
    17: 10,
}

FIELDNAMES = ['name', 'github_url', 'project_description'] + [f'act_sdg{i}' for i in range(1, 18)] + [f'pred_readme_sdg{i}' for i in range(1, 18)]


def parse_sdgs(item):
    present = []
    for entry in item.get('sdgs') or []:
        if isinstance(entry, dict):
            raw = entry.get('number')
        else:
            raw = entry
        if raw is None:
            continue
        match = re.search(r'(\d+)', str(raw))
        if not match:
            continue
        n = int(match.group(1))
        if 1 <= n <= 17:
            present.append(n)
    return present


def clean_repo_url(raw_url):
    if not raw_url:
        return ''
    value = str(raw_url).strip()
    if not value:
        return ''
    try:
        parsed = urlparse(value)
    except Exception:
        return ''

    host = (parsed.netloc or parsed.path).lower()
    if host.startswith('www.'):
        host = host[4:]
    if host in ALLOWED_REPO_HOSTS:
        return value
    return ''


def main():
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    data = response.json()

    selected = []
    seen = set()
    counts = Counter()

    for _ in range(70):
        best_item = None
        best_present = []
        best_score = None

        for item in data:
            name = item.get('name') or ''
            if name in seen:
                continue

            present = parse_sdgs(item)
            if not present:
                continue

            score = 0.0
            for sdg in present:
                deficit = max(TARGET_COUNT[sdg] - counts[sdg], 0)
                score += deficit * 5
                if counts[sdg] == 0:
                    score += 2
                elif counts[sdg] >= TARGET_COUNT[sdg]:
                    score -= 4
            score += sum(1 for sdg in present if counts[sdg] < TARGET_COUNT[sdg]) * 0.5

            if best_score is None or score > best_score:
                best_score = score
                best_item = item
                best_present = present

        if best_item is None:
            break

        seen.add(best_item.get('name') or '')
        selected.append((best_item, best_present))
        for sdg in best_present:
            counts[sdg] += 1

    rows = []
    for item, present in selected:
        name = item.get('name') or ''
        github_metrics = item.get('githubMetrics') or {}
        raw_github_url = next(iter(github_metrics.keys()), None) if github_metrics else (item.get('sourceURL') or '')
        github_url = clean_repo_url(raw_github_url)
        sdg_relevance = item.get('sdgRelevance')
        if isinstance(sdg_relevance, dict):
            description = ' '.join(str(v) for v in sdg_relevance.values() if v is not None)
        else:
            description = str(sdg_relevance or '')
        description = ' '.join(description.split())

        row = {'name': name, 'github_url': github_url, 'project_description': description}
        for i in range(1, 18):
            row[f'act_sdg{i}'] = '1' if i in present else '0'
        for i in range(1, 18):
            row[f'pred_readme_sdg{i}'] = '0.0'
        rows.append(row)

    with OUT_PATH.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print('rows_written', len(rows))
    for i in range(1, 18):
        count = sum(1 for row in rows if row.get(f'act_sdg{i}') == '1')
        print(f'SDG{i}: {count}')


if __name__ == '__main__':
    main()
