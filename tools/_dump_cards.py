# -*- coding: utf-8 -*-
"""Вытаскивает из ui_game.txt длинные описательные пары EN=RU (карточки видов,
описания геймплея и пр.) для QA-ревью перевода. Печатает JSON-массив."""
import os, json

ROOT = os.path.join(os.path.dirname(__file__), '..')
TXT = os.path.join(ROOT, 'BepInEx', 'Translation', 'ru', 'Text', 'ui_game.txt')

pairs = []
with open(TXT, encoding='utf-8') as f:
    for i, raw in enumerate(f, 1):
        line = raw.rstrip('\n')
        if not line or line.startswith('//'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        # карточки = многобуллетные описания (содержат литеральный "\n- ")
        # либо просто длинные строки (>120 симв. источника)
        is_card = ('\\n- ' in k) or ('\\n-' in k and k.lstrip().startswith('- '))
        if is_card or len(k) > 160:
            pairs.append({
                'line': i,
                'en_len': len(k),
                'ru_len': len(v),
                'en': k,
                'ru': v,
            })

print(json.dumps(pairs, ensure_ascii=False, indent=1))
import sys
sys.stderr.write(f"\n[dump] cards found: {len(pairs)}\n")
