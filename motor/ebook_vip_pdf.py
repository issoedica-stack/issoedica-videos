#!/usr/bin/env python3
"""Ebook VIP semanal (Notion) -> PDF on-brand Isso É Dica.
Uso: python3 ebook_vip_pdf.py <conteudo.md> <saida.pdf> "<titulo>" <numero> "<mes/ano>" "<emoji>"
O .md é o corpo da subpágina do Notion (formato do notion-fetch).
"""
import re, sys, html
from playwright.sync_api import sync_playwright

src, out, title, num, mesano, emoji = sys.argv[1:7]
md = open(src, encoding="utf-8").read()

def inline(t):
    t = html.escape(t, quote=False)
    t = t.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    t = t.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<a href='\2'>\1</a>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t

parts, lines, i = [], md.splitlines(), 0
inlist = None
def close():
    global inlist
    if inlist: parts.append(f"</{inlist}>"); inlist = None
while i < len(lines):
    l = lines[i]
    if l.startswith("```"):
        close(); i += 1; buf = []
        while i < len(lines) and not lines[i].startswith("```"):
            buf.append(lines[i]); i += 1
        parts.append("<div class='prompt'><div class='ptag'>PROMPT · COPIE E COLE</div><pre>" + html.escape("\n".join(buf)) + "</pre></div>")
    elif l.startswith("## "):
        close(); h = l[3:]
        m = re.match(r"(\d+)\.\s+(.*)", h)
        if m: parts.append(f"<h2><span class='n'>{m.group(1)}</span>{inline(m.group(2))}</h2>")
        else: parts.append(f"<h2>{inline(h)}</h2>")
    elif l.startswith("> "):
        close(); parts.append(f"<div class='badge'>{inline(l[2:])}</div>")
    elif re.match(r"^\d+\.\s", l):
        if inlist != "ol": close(); parts.append("<ol>"); inlist = "ol"
        parts.append(f"<li>{inline(re.sub(r'^\d+\.\s','',l))}</li>")
    elif l.startswith("- "):
        if inlist != "ul": close(); parts.append("<ul>"); inlist = "ul"
        parts.append(f"<li>{inline(l[2:])}</li>")
    elif l.strip() == "":
        close()
    elif l.strip() == "<b>Prompt pronto (copie e cole):</b>":
        pass
    elif l.strip() == "<i>Isso É Dica</i>":
        pass
    else:
        close(); parts.append(f"<p>{inline(l)}</p>")
    i += 1
close()
body = "\n".join(parts)

doc = f"""<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><style>
@page {{ size: A4; margin: 16mm 15mm 18mm 15mm; }}
@page :first {{ margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; color: #1b1d2b; font-size: 10.6pt; line-height: 1.55; margin: 0; }}
.cover {{ height: 297mm; width: 210mm; background: radial-gradient(circle at 80% 15%, #6d3bff 0%, transparent 45%), radial-gradient(circle at 10% 90%, #1f6bff 0%, transparent 50%), #0b0f2e; color: #fff; padding: 26mm 20mm; display: flex; flex-direction: column; page-break-after: always; }}
.cover .brand {{ font-family: Poppins; font-weight: 700; letter-spacing: .08em; font-size: 12pt; opacity: .9; }}
.cover .ed {{ margin-top: 48mm; display: inline-block; background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.25); border-radius: 30px; padding: 6px 16px; font-size: 10pt; letter-spacing: .1em; align-self: flex-start; }}
.cover .emoji {{ font-size: 54pt; margin-top: 12mm; }}
.cover h1 {{ font-family: Poppins; font-size: 32pt; line-height: 1.15; margin: 8mm 0 0; }}
.cover .sub {{ margin-top: 8mm; font-size: 13pt; opacity: .85; max-width: 150mm; }}
.cover .foot {{ margin-top: auto; display: flex; justify-content: space-between; font-size: 10pt; opacity: .8; border-top: 1px solid rgba(255,255,255,.2); padding-top: 6mm; }}
.badge {{ background: #f1edff; color: #4b2bd1; border-radius: 8px; padding: 8px 12px; font-size: 9pt; margin-bottom: 6mm; }}
h2 {{ font-family: Poppins; font-size: 15pt; color: #0b0f2e; margin: 9mm 0 3mm; page-break-after: avoid; border-left: 4px solid #6d3bff; padding-left: 10px; }}
h2 .n {{ display: inline-block; background: linear-gradient(135deg,#6d3bff,#1f6bff); color: #fff; width: 26px; height: 26px; border-radius: 50%; text-align: center; line-height: 26px; font-size: 11pt; margin-right: 8px; }}
p {{ margin: 0 0 3mm; }}
ol, ul {{ margin: 0 0 3mm; padding-left: 7mm; }}
li {{ margin-bottom: 1.5mm; }}
a {{ color: #4b2bd1; word-break: break-all; }}
.prompt {{ background: #0f1330; color: #e8e9ff; border-radius: 10px; padding: 12px 14px; margin: 3mm 0 5mm; page-break-inside: avoid; }}
.ptag {{ font-size: 7.5pt; letter-spacing: .14em; color: #a99bff; font-weight: 700; margin-bottom: 6px; }}
pre {{ margin: 0; white-space: pre-wrap; font-family: 'DejaVu Sans Mono', monospace; font-size: 8.6pt; line-height: 1.5; }}
</style></head><body>
<section class='cover'>
<div class='brand'>ISSO É DICA</div>
<div class='ed'>BÔNUS VIP · EDIÇÃO {num} · {html.escape(mesano.upper())}</div>
<div class='emoji'>{emoji}</div>
<h1>{html.escape(title)}</h1>
<div class='sub'>Guia prático com prompts prontos para copiar e colar.</div>
<div class='foot'><span>@issoedica</span><span>Grupo VIP Isso É Dica</span></div>
</section>
<main>{body}</main>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.set_content(doc, wait_until="load")
    pg.pdf(path=out, format="A4", print_background=True,
           display_header_footer=True, header_template="<span></span>",
           footer_template="<div style='font-size:7pt;width:100%;text-align:center;color:#888;font-family:Inter'>Isso É Dica · @issoedica · <span class='pageNumber'></span></div>")
    b.close()
print("ok", out)
