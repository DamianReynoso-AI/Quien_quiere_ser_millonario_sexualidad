import json, random, html, sys, collections
sys.path.insert(0, sys.argv[1]) if len(sys.argv) > 1 else None
from preguntas import Q

random.seed(2026)
LET = "ABCD"
data = []
# repartir la posición correcta de forma balanceada
pos_cycle = []
for n, (nivel, tema, preg, ops, exp, src) in enumerate(Q, 1):
    if not pos_cycle:
        pos_cycle = [0, 1, 2, 3]; random.shuffle(pos_cycle)
    c = pos_cycle.pop()
    inc = ops[1:][:]
    random.shuffle(inc)
    final = inc[:c] + [ops[0]] + inc[c:]
    data.append(dict(id=n, nivel=nivel, tema=tema, pregunta=preg, opciones=final, c=c, explicacion=exp, fuente=src))

tpl = open("plantilla.html", encoding="utf-8").read()
out = tpl.replace("/*__PREGUNTAS__*/[]", json.dumps(data, ensure_ascii=False, indent=0))
open("../index.html", "w", encoding="utf-8").write(out)

# ---------- guía PDF (HTML para imprimir) ----------
cnt = collections.Counter(d["nivel"] for d in data)
temas = collections.OrderedDict()
for d in data:
    temas.setdefault(d["tema"], 0); temas[d["tema"]] += 1
fuentes = sorted(set(d["fuente"] for d in data))
NT = {1: "Nivel 1 · Preguntas fáciles", 2: "Nivel 2 · Preguntas intermedias", 3: "Nivel 3 · Preguntas difíciles"}
e = html.escape
parts = []
num = 0
for nivel in (1, 2, 3):
    parts.append(f'<h2 class="lvl">{NT[nivel]}</h2>')
    for d in [x for x in data if x["nivel"] == nivel]:
        num += 1
        ops = "".join(f'<li class="{"ok" if i == d["c"] else ""}"><b>{LET[i]})</b> {e(o)}</li>' for i, o in enumerate(d["opciones"]))
        parts.append(f'''<div class="q"><div class="qh"><span class="n">{num}</span><span class="t">{e(d["tema"])}</span></div>
<p class="qq">{e(d["pregunta"])}</p><ul>{ops}</ul>
<p class="ans"><b>Respuesta:</b> {LET[d["c"]]}) {e(d["opciones"][d["c"]])}</p>
<p class="ex">{e(d["explicacion"])}</p><p class="src">Fuente: {e(d["fuente"])}</p></div>''')

guia = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guía de preguntas con respuestas</title>
<style>
@page{{size:Letter;margin:18mm 16mm}}
body{{font-family:"Segoe UI",Roboto,Arial,sans-serif;color:#1d1640;font-size:10.5pt;line-height:1.4}}
.cover{{height:240mm;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;page-break-after:always}}
.cover .disc{{width:110px;height:110px;border-radius:50%;background:#2a1a7a;border:5px solid #e0a820;color:#f6c445;font-size:54px;font-weight:900;display:grid;place-items:center;line-height:110px}}
.cover h1{{font-size:30pt;margin:18px 0 4px;color:#2a1a7a}}
.cover h2{{font-size:16pt;margin:0;color:#7a5a00;font-weight:600}}
.cover .meta{{margin-top:40px;font-size:12pt;text-align:left;width:120mm}}
.cover .meta div{{border-bottom:1px solid #999;padding:8px 0}}
h2.lvl{{background:#2a1a7a;color:#fff;padding:8px 12px;border-radius:6px;font-size:14pt;margin:18px 0 10px;page-break-after:avoid}}
h2.sec{{color:#2a1a7a;border-bottom:2px solid #e0a820;padding-bottom:4px}}
.q{{border:1px solid #d8d3f0;border-left:5px solid #e0a820;border-radius:6px;padding:8px 12px;margin-bottom:9px;page-break-inside:avoid}}
.qh{{display:flex;gap:8px;align-items:center;margin-bottom:3px}}
.qh .n{{background:#2a1a7a;color:#fff;font-weight:800;border-radius:50%;width:24px;height:24px;display:inline-grid;place-items:center;font-size:9.5pt;line-height:24px;text-align:center}}
.qh .t{{color:#7a5a00;font-size:9pt;text-transform:uppercase;letter-spacing:.04em;font-weight:700}}
.qq{{font-weight:700;margin:2px 0 4px}}
ul{{list-style:none;padding:0;margin:0 0 4px;columns:2;column-gap:16px}}
li{{margin-bottom:2px;break-inside:avoid}}
li.ok{{font-weight:700;color:#0b6b37}}
.ans{{margin:4px 0 2px;color:#0b6b37}}
.ex{{margin:2px 0;color:#333}}
.src{{margin:2px 0 0;color:#666;font-size:8.8pt;font-style:italic}}
table{{border-collapse:collapse;width:100%;font-size:10pt}}td,th{{border:1px solid #ccc;padding:4px 8px;text-align:left}}th{{background:#efeafc}}
</style></head><body>
<div class="cover"><div class="disc">?</div>
<h1>Guía de preguntas con respuestas</h1>
<h2>Juego “¿Quién Quiere Ser Sexperto?” · Afectividad y Sexualidad</h2>
<p style="margin-top:14px">{len(data)} preguntas obtenidas de los materiales de clase del semestre</p>
<div class="meta"><div><b>Equipo:</b></div><div><b>Integrantes:</b></div><div><b>Profesor(a):</b></div><div><b>Fecha:</b></div></div></div>

<h2 class="sec">Contenido</h2>
<p>La guía reúne {len(data)} preguntas de opción múltiple ({cnt[1]} fáciles, {cnt[2]} intermedias y {cnt[3]} difíciles), cada una con su respuesta correcta, una breve explicación y la fuente del curso de donde se obtuvo. Es la base que alimenta el juego: las preguntas fáciles corresponden a la parte baja de la escalera de premios y las difíciles a la parte alta.</p>
<table><tr><th>Tema</th><th>Preguntas</th></tr>{"".join(f"<tr><td>{e(t)}</td><td>{n}</td></tr>" for t, n in temas.items())}</table>
<h2 class="sec">Materiales de clase utilizados</h2>
<ul style="columns:1">{"".join(f"<li>• {e(f)}</li>" for f in fuentes)}</ul>
<div style="page-break-after:always"></div>
{"".join(parts)}
</body></html>'''
open("guia.html", "w", encoding="utf-8").write(guia)
print(len(data), dict(cnt), collections.Counter(d["c"] for d in data))
