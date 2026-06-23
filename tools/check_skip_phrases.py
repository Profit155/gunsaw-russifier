# -*- coding: utf-8 -*-
"""Проверка: не упущен ли текстоподобный контент в skip."""
import io, glob, json, re

key2tag = {}
for fp in glob.glob('docs/wf_batches/*.tsv'):
    for ln in io.open(fp, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if '\t' in ln:
            k, t = ln.rsplit('\t', 1)
            key2tag[k] = t

skip = []
for fp in glob.glob('docs/wf_out/out_*.json'):
    for r in json.load(io.open(fp, encoding='utf-8')):
        if r.get('verdict') == 'skip':
            skip.append(r['key'])
print('skip всего (из workflow):', len(skip))


def is_path(k):
    return k.startswith(('Sounds/', 'Spawnables/', 'Assets/', 'Enemies/', '/')) or '/' in k or '\\' in k


def phrase(k):
    if is_path(k):
        return False
    words = re.findall(r'[A-Za-z]+', k)
    return k.count(' ') >= 2 and len(words) >= 3


susp = [k for k in skip if phrase(k)]
print('skip, ВЫГЛЯДЯЩИХ как фраза (возможно упущенный текст):', len(susp))
for k in susp[:50]:
    print('  [%s] %r' % (key2tag.get(k, '?'), k[:75]))
