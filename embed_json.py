import json, re

with open('data/crm.json', encoding='utf-8') as f:
    leads = json.load(f)

# Serializa como string JSON compacta, ASCII-safe
json_str = json.dumps(leads, ensure_ascii=False, separators=(',', ':'))

# Duplo-encode: json.dumps na string escapa " e \ e unicode -> seguro em JS
js_literal = json.dumps(json_str, ensure_ascii=True)
# Escapa </ para evitar que o HTML parser feche a tag <script> prematuramente
js_literal = js_literal.replace('</', '<\\/')

with open('index.html', encoding='utf-8') as f:
    html = f.read()

# Usa str.replace com posicoes para evitar o re.sub interpretar \u como escape
old_pattern = '"data/crm.json": { url: "data/crm.json" }'
new_entry = '"data/crm.json": { content: ' + js_literal + ' }'

# Tenta substituicao simples primeiro
if old_pattern in html:
    html = html.replace(old_pattern, new_entry)
else:
    # Tenta regex sem usar re.sub (replace manual)
    m = re.search(r'"data/crm\.json":\s*\{[^}]*\}', html)
    if m:
        html = html[:m.start()] + new_entry + html[m.end():]
    else:
        print('ERRO: padrao nao encontrado')
        raise SystemExit(1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'OK — {len(leads)} leads embutidos com encoding seguro')
print(f'Tamanho index.html: {len(html.encode("utf-8"))//1024} KB')
