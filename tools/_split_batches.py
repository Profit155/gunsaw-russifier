# -*- coding: utf-8 -*-
"""Режет docs/_review_corpus.json на батч-файлы по тирам для ревью.
Пишет docs/_review_batches/<tier>_<nn>.json и манифест docs/_review_manifest.json."""
import os, json, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
CORPUS = os.path.join(ROOT, 'docs', '_review_corpus.json')
OUTDIR = os.path.join(ROOT, 'docs', '_review_batches')
os.makedirs(OUTDIR, exist_ok=True)

with open(CORPUS, encoding='utf-8') as f:
    rows = json.load(f)

# Чистим старые батчи
for fn in os.listdir(OUTDIR):
    if fn.endswith('.json'):
        os.remove(os.path.join(OUTDIR, fn))

tiers = {'long': [], 'regex': [], 'short': []}
for r in rows:
    tiers[r['kind']].append(r)

SIZE = {'long': 2, 'regex': 18, 'short': 30}
manifest = []
for tier, items in tiers.items():
    sz = SIZE[tier]
    for bi in range(0, len(items), sz):
        chunk = items[bi:bi+sz]
        nn = len(manifest)
        path = os.path.join(OUTDIR, f"{tier}_{nn:03d}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        manifest.append({'path': os.path.abspath(path), 'tier': tier, 'n': len(chunk)})

# Сводный файл всех длинных (для сверки согласованности)
long_all = os.path.abspath(os.path.join(ROOT, 'docs', '_review_long_all.json'))
with open(long_all, 'w', encoding='utf-8') as f:
    json.dump(tiers['long'], f, ensure_ascii=False, indent=1)

man_path = os.path.join(ROOT, 'docs', '_review_manifest.json')
with open(man_path, 'w', encoding='utf-8') as f:
    json.dump({'batches': manifest, 'long_all': long_all}, f, ensure_ascii=False, indent=1)

sys.stderr.write(f"[split] batches={len(manifest)} "
                 f"(long={sum(1 for m in manifest if m['tier']=='long')} "
                 f"regex={sum(1 for m in manifest if m['tier']=='regex')} "
                 f"short={sum(1 for m in manifest if m['tier']=='short')}) "
                 f"manifest={man_path}\n")
print(man_path)
