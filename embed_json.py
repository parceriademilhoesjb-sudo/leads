import json, re

with open('data/crm.json', encoding='utf-8') as f:
    leads = json.load(f)

minified = json.dumps(leads, ensure_ascii=False, separators=(',',':'))

with open('index.html', encoding='utf-8') as f:
    html = f.read()

old = '"data/crm.json": { url: "data/crm.json" }'
new = '"data/crm.json": { content: JSON.stringify(' + minified + ') }'

if old in html:
    html = html.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'OK — {len(leads)} leads embutidos no index.html')
else:
    print('ERRO: padrao nao encontrado no index.html')
