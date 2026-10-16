#!/usr/bin/env python3
"""Isso É Dica: gerador de ebook vendável (Clube / Hotmart).
Uso: python3 ebook_builder.py spec.json saida_dir [links.json]
Gera: <slug>.pdf (capa + miolo), <slug>-capa-quadrada.png (1200x1200, Hotmart),
<slug>-capa-vertical.png (1600x2560, Amazon/Kindle), <slug>-capa-a4.png.
links.json (opcional) sobrescreve: clube, metodo, negocio, afiliacao, grupo, mentoria.
"""
import json, sys, html, os, asyncio, re
from pathlib import Path
from pypdf import PdfWriter, PdfReader

E = html.escape

DEFAULT_LINKS = {
    "grupo": "https://chat.whatsapp.com/FFo2sGke1MsEAz6sqhnvC4",
    "mentoria": "https://bit.ly/mentoria-issoedica",
    "instagram": "https://instagram.com/issoedica",
    "youtube": "https://youtube.com/@issoedica1375",
    "clube": "",      # link Hotmart do Clube (preencher)
    "metodo": "",     # link Hotmart do Método Invisível
    "negocio": "",    # link Hotmart do IA no Negócio
    "afiliacao": "",  # link de afiliação Hotmart deste produto
}
FERRAMENTAS = [
    ("Tess AI", "As melhores IAs (ChatGPT, Claude, Gemini e mais) num lugar só, em português.", "https://tess.cello.so/HXcXrqw3o6o"),
    ("ElevenLabs", "Voz e narração com IA realista, inclusive com a sua voz clonada.", "https://try.elevenlabs.io/2c3sevzh43le"),
    ("Higgsfield", "Vídeos e imagens com IA em qualidade de cinema para redes sociais.", "https://higgsfield.ai?fpr=antonio-cd928a"),
    ("OpusClip", "Transforma vídeos longos em cortes curtos com legenda, no automático.", "https://tolt.link/httpsopusproviaantoniono"),
    ("Hostinger", "Site, domínio e criador de sites com IA para ter sua casa na internet.", "https://www.hostinger.com/br?REFERRALCODE=8CZISSOEDPQM"),
]

CSS = r"""
@page { size: A4; margin: 22mm 18mm 20mm 18mm; }
:root{--navy:#0b1030;--blue:#1d2a8a;--purple:#6b2bd9;--acc:#7c5cff;--yellow:#ffd23f;--ink:#1a1d2e;--mut:#5b6075;--line:#e6e7f0;--soft:#f4f2ff}
*{box-sizing:border-box}
body{font-family:'Inter',sans-serif;color:var(--ink);font-size:11.6pt;line-height:1.66;margin:0}
h1,h2,h3{font-family:'Poppins',sans-serif;line-height:1.2;margin:0}
p{margin:0 0 9pt}
.page{page-break-before:always}
.kicker{font-family:'Poppins';font-weight:700;font-size:9pt;letter-spacing:.14em;color:var(--purple);text-transform:uppercase;margin-bottom:6pt}
h1.sec{font-size:24pt;font-weight:800;color:var(--navy);margin-bottom:14pt}
h2{font-size:14.5pt;font-weight:700;color:var(--navy);margin:16pt 0 7pt}
.chap-open{background:linear-gradient(135deg,#0b1030 0%,#1d2a8a 55%,#6b2bd9 100%);color:#fff;border-radius:14pt;padding:26pt 24pt;margin-bottom:16pt;position:relative;overflow:hidden}
.chap-open .num{font-family:'Poppins';font-weight:800;font-size:54pt;line-height:1;color:rgba(255,255,255,.18);position:absolute;right:18pt;top:10pt}
.chap-open .lab{font-family:'Poppins';font-weight:700;font-size:9pt;letter-spacing:.16em;color:var(--yellow)}
.chap-open h1{font-size:22pt;font-weight:800;margin-top:6pt;max-width:80%}
ol.steps{counter-reset:s;list-style:none;padding:0;margin:0 0 8pt}
ol.steps li{counter-increment:s;position:relative;padding-left:28pt;margin-bottom:7pt}
ol.steps li:before{content:counter(s);position:absolute;left:0;top:1pt;width:19pt;height:19pt;border-radius:50%;background:var(--acc);color:#fff;font-family:'Poppins';font-weight:700;font-size:9pt;text-align:center;line-height:19pt}
.prompt{background:#0f1430;border-radius:10pt;padding:12pt 14pt 13pt;margin:10pt 0 12pt;page-break-inside:avoid}
.prompt .pl{font-family:'Poppins';font-weight:700;font-size:8.5pt;letter-spacing:.12em;color:var(--yellow);margin-bottom:6pt}
.prompt pre{white-space:pre-wrap;font-family:'JetBrains Mono','DejaVu Sans Mono',monospace;font-size:9.4pt;line-height:1.55;color:#e9ebff;margin:0}
.box{border-radius:10pt;padding:11pt 14pt;margin:10pt 0;page-break-inside:avoid}
.box .bt{font-family:'Poppins';font-weight:700;font-size:10pt;margin-bottom:4pt}
.ex{background:var(--soft);border-left:4pt solid var(--acc)}
.ex .bt{color:var(--purple)}
.err{background:#fff4f2;border-left:4pt solid #f06449}
.err .bt{color:#c2412b}
.err ul{margin:0;padding-left:15pt}
.tool{background:#fffbea;border:1.2pt solid #f5d76e}
.tool .bt{color:#8a6a00}
.tool a,.cta a,.next a{color:var(--purple);font-weight:600;text-decoration:none}
.check{border:1.2pt dashed #c9c3ff;background:#fbfaff}
.check .bt{color:var(--navy)}
.check ul,.cl ul{list-style:none;padding:0;margin:0}
.check li,.cl li{padding-left:20pt;position:relative;margin-bottom:4pt}
.check li:before,.cl li:before{content:'';position:absolute;left:0;top:3pt;width:11pt;height:11pt;border:1.6pt solid var(--acc);border-radius:3pt}
.toc{list-style:none;padding:0;margin:0}
.toc li{display:flex;align-items:baseline;border-bottom:1pt solid var(--line);padding:8pt 0;font-size:11.5pt}
.toc .n{font-family:'Poppins';font-weight:800;color:var(--acc);width:34pt}
.lead{font-size:12.3pt;color:#2d3150}
table{width:100%;border-collapse:collapse;font-size:9.8pt;margin:8pt 0}
td,th{border:1pt solid var(--line);padding:7pt 8pt;text-align:left;vertical-align:top}
th{background:var(--soft);font-family:'Poppins';font-weight:600;color:var(--navy)}
.tpl pre{white-space:pre-wrap;font-family:'Inter';font-size:10pt;line-height:1.55;background:var(--soft);border-radius:10pt;padding:12pt 14pt;margin:6pt 0 14pt;color:#262a45;page-break-inside:avoid}
.toolcard{display:flex;gap:12pt;align-items:flex-start;border:1pt solid var(--line);border-radius:10pt;padding:10pt 12pt;margin-bottom:8pt;page-break-inside:avoid}
.toolcard .tn{font-family:'Poppins';font-weight:700;color:var(--navy);width:88pt;flex:none}
.toolcard .td{flex:1;font-size:10.2pt}
.toolcard .tl{font-size:9pt;color:var(--purple);word-break:break-all}
.cta{background:linear-gradient(135deg,#0b1030,#1d2a8a 60%,#6b2bd9);color:#fff;border-radius:14pt;padding:18pt 20pt;margin:12pt 0;page-break-inside:avoid}
.cta h3{font-size:15pt;font-weight:800;margin-bottom:6pt}
.cta p{color:#dfe2ff}
.cta .btn{display:inline-block;background:var(--yellow);color:#151a3a;font-family:'Poppins';font-weight:800;font-size:10.5pt;border-radius:30pt;padding:7pt 16pt;margin-top:4pt;text-decoration:none}
.next{border:1.2pt solid var(--line);border-radius:12pt;padding:12pt 15pt;margin-bottom:9pt;page-break-inside:avoid}
.next .tag{font-family:'Poppins';font-weight:700;font-size:8.5pt;letter-spacing:.12em;color:var(--purple)}
.next h3{font-size:12.5pt;color:var(--navy);margin:3pt 0 4pt}
.small{font-size:9pt;color:var(--mut)}
.legal{font-size:8.6pt;color:var(--mut);margin-top:14pt;border-top:1pt solid var(--line);padding-top:8pt}
"""

COVER_CSS = r"""
@page{size:A4;margin:0}
*{box-sizing:border-box}html,body{margin:0}
.cv{width:210mm;height:297mm;position:relative;overflow:hidden;background:radial-gradient(120% 80% at 85% 10%,#6b2bd9 0%,rgba(107,43,217,0) 55%),radial-gradient(90% 70% at 0% 100%,#1d2a8a 0%,rgba(29,42,138,0) 60%),#0b1030;color:#fff;font-family:'Poppins',sans-serif}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:14mm 14mm}
.orb{position:absolute;border-radius:50%;filter:blur(2px)}
.o1{width:150mm;height:150mm;right:-55mm;top:58mm;border:1.2mm solid rgba(124,92,255,.35)}
.o2{width:95mm;height:95mm;right:-22mm;top:86mm;border:.8mm solid rgba(255,210,63,.35)}
.o3{width:40mm;height:40mm;right:24mm;top:118mm;background:radial-gradient(circle,#ffd23f 0%,#ff9f1c 70%);box-shadow:0 0 30mm rgba(255,210,63,.55)}
.logo{position:absolute;left:18mm;top:18mm;display:flex;align-items:center;gap:3mm}
.pill{border:.6mm solid #7c5cff;background:rgba(255,255,255,.07);border-radius:20mm;padding:2.6mm 6mm;font-weight:800;letter-spacing:.06em;font-size:13pt}
.pill b{color:#ffd23f}
.handle{font-weight:600;font-size:10pt;color:#b9bdf0}
.vol{position:absolute;right:18mm;top:20mm;font-weight:700;font-size:9pt;letter-spacing:.2em;color:#ffd23f;text-align:right}
.title{position:absolute;left:18mm;top:66mm;width:150mm}
.title .k{font-weight:700;letter-spacing:.2em;font-size:10pt;color:#b9bdf0;margin-bottom:5mm}
.title h1{margin:0;font-weight:800;font-size:44pt;line-height:1.02;letter-spacing:-.01em}
.title h1 .hl{color:#ffd23f}
.sub{position:absolute;left:18mm;top:178mm;width:122mm;font-family:'Inter';font-size:13.5pt;line-height:1.45;color:#e3e5ff}
.selo{position:absolute;left:18mm;top:212mm;display:inline-block;background:#ffd23f;color:#141938;font-weight:800;font-size:11pt;border-radius:4mm;padding:3.4mm 5mm;max-width:150mm}
.cta{position:absolute;left:18mm;bottom:30mm;width:170mm;font-weight:600;font-size:12pt;color:#fff;border-left:1.2mm solid #7c5cff;padding-left:4mm}
.foot{position:absolute;left:18mm;right:18mm;bottom:13mm;display:flex;justify-content:space-between;font-size:8.5pt;letter-spacing:.14em;color:#8f94c9;font-weight:600}
"""

FONTS = "<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;600&display=swap' rel='stylesheet'>"


def p_list(ps):
    return "".join(f"<p>{E(x)}</p>" for x in ps)


def prompt_block(txt, label="PROMPT PRONTO · COPIE E COLE"):
    return f"<div class='prompt'><div class='pl'>{label}</div><pre>{E(txt)}</pre></div>"


def link_or_kw(url, kw):
    if url:
        return f"<a href='{E(url)}'>{E(url.replace('https://',''))}</a>"
    return f"chame <b>@issoedica</b> no Instagram e mande a palavra <b>{kw}</b>"


def cover_html(s):
    lines = s["titulo_capa"]
    h = "<br>".join(E(l) for l in lines[:-1]) + f"<br><span class='hl'>{E(lines[-1])}</span>"
    return f"""<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{COVER_CSS}</style></head><body>
<div class='cv'><div class='grid'></div><div class='orb o1'></div><div class='orb o2'></div><div class='orb o3'></div>
<div class='logo'><div class='pill'>ISSO <b>É</b> DICA</div><div class='handle'>@issoedica</div></div>
<div class='vol'>COLEÇÃO IA NA PRÁTICA<br>VOL. {E(s['nn'])}</div>
<div class='title'><div class='k'>GUIA PRÁTICO</div><h1>{h}</h1></div>
<div class='sub'>{E(s['subtitulo'])}</div>
<div class='selo'>{E(s['selo_capa'])}</div>
<div class='cta'>{E(s['cta_capa'])}</div>
<div class='foot'><span>ISSO É DICA</span><span>{E(s['mesano'].upper())}</span></div>
</div></body></html>"""


def body_html(s, L):
    fp = s["ferramenta_principal"]
    out = []
    # Como usar + sumário
    toc = "".join(f"<li><span class='n'>{i:02d}</span>{E(c['titulo'])}</li>" for i, c in enumerate(s["capitulos"], 1))
    toc += f"<li><span class='n'>+</span>Bônus: {E(s['bonus']['titulo'].replace('Bônus: ',''))}</li><li><span class='n'>+</span>Modelos prontos para copiar</li><li><span class='n'>+</span>Perguntas frequentes</li><li><span class='n'>+</span>Plano de 7 dias e checklist final</li>"
    out.append(f"""<div><div class='kicker'>Coleção IA na Prática · Vol. {E(s['nn'])}</div><h1 class='sec'>{E(s['titulo'])}</h1>
<p class='lead'>{E(s['subtitulo'])}.</p>
<h2>O que tem neste guia</h2><ul class='toc'>{toc}</ul>
<h2>Como usar</h2><ol class='steps'>{''.join(f'<li>{E(x)}</li>' for x in s['como_usar'])}</ol></div>""")
    # Introdução
    out.append(f"""<div class='page'><div class='kicker'>Introdução</div><h1 class='sec'>Por que agora</h1>{p_list(s['intro'])}
<div class='box ex'><div class='bt'>Nosso exemplo ao longo do guia</div>{E(s['persona'])}</div></div>""")
    # Contexto
    c = s["contexto"]
    out.append(f"""<div class='page'><div class='kicker'>Antes de começar</div><h1 class='sec'>2 minutos que mudam tudo</h1><p>{E(c['texto'])}</p>
<ol class='steps'>{''.join(f'<li>{E(x)}</li>' for x in c['passos'])}</ol>{prompt_block(c['prompt'],'CONTEXTO BASE · COLE PRIMEIRO')}
<div class='box tool'><div class='bt'>⚡ Ferramenta recomendada: {E(fp['nome'])}</div>{E(fp['porque'])}<br><a href='{E(fp['link'])}'>{E(fp['link'].replace('https://',''))}</a> <span class='small'>(link de parceiro)</span></div></div>""")
    # Capítulos
    for i, ch in enumerate(s["capitulos"], 1):
        parts = [f"<div class='page'><div class='chap-open'><div class='num'>{i:02d}</div><div class='lab'>CAPÍTULO {i:02d}</div><h1>{E(ch['titulo'])}</h1></div>"]
        parts.append(p_list(ch["porque"]))
        parts.append("<h2>Passo a passo</h2><ol class='steps'>" + "".join(f"<li>{E(x)}</li>" for x in ch["passos"]) + "</ol>")
        parts.append(prompt_block(ch["prompt"]))
        if ch.get("prompt_extra"):
            parts.append(prompt_block(ch["prompt_extra"], E(ch.get("prompt_extra_titulo", "PROMPT EXTRA")).upper()))
        if ch.get("ferramenta_contexto"):
            t = ch["ferramenta_contexto"]
            parts.append(f"<div class='box tool'><div class='bt'>⚡ Atalho: {E(t['nome'])}</div>{E(t['texto'])} <a href='{E(t['link'])}'>{E(t['link'].replace('https://',''))}</a> <span class='small'>(link de parceiro)</span></div>")
        parts.append(f"<div class='box ex'><div class='bt'>Exemplo aplicado</div>{E(ch['exemplo'])}</div>")
        parts.append("<div class='box err'><div class='bt'>Erros que travam as vendas</div><ul>" + "".join(f"<li>{E(x)}</li>" for x in ch["erros"]) + "</ul></div>")
        parts.append("<div class='box check'><div class='bt'>Checklist do capítulo</div><ul>" + "".join(f"<li>{E(x)}</li>" for x in ch["checklist"]) + "</ul></div></div>")
        out.append("".join(parts))
    # Bônus
    b = s["bonus"]
    extra = ""
    if b.get("extra"):
        extra = f"<div class='box tool'><div class='bt'>⚡ {E(b.get('extra_nome','Ideia extra'))}</div>{E(b['extra'])} <a href='{E(b['extra_link'])}'>{E(b['extra_link'].replace('https://',''))}</a> <span class='small'>(link de parceiro)</span></div>"
    out.append(f"<div class='page'><div class='chap-open'><div class='num'>+</div><div class='lab'>BÔNUS</div><h1>{E(b['titulo'].replace('Bônus: ',''))}</h1></div>{p_list(b['texto'])}{prompt_block(b['prompt'])}{extra}</div>")
    # Modelos
    mm = ["<div class='page'><div class='kicker'>Modelos prontos</div><h1 class='sec'>Copie, preencha e use</h1>"]
    for m in s["modelos"]:
        mm.append(f"<h2>{E(m['titulo'])}</h2>")
        if m.get("texto"):
            mm.append(f"<div class='tpl'><pre>{E(m['texto'])}</pre></div>")
        if m.get("tabela"):
            t = m["tabela"]
            mm.append("<table><tr>" + "".join(f"<th>{E(x)}</th>" for x in t[0]) + "</tr>" + "".join("<tr>" + "".join(f"<td>{E(x) or '&nbsp;'}</td>" for x in r) + "</tr>" for r in t[1:]) + "</table>")
    mm.append("</div>")
    out.append("".join(mm))
    # FAQ
    if s.get("faq"):
        fq = "".join(f"<h2>{E(q)}</h2><p>{E(a)}</p>" for q, a in s["faq"])
        out.append(f"<div class='page'><div class='kicker'>Dúvidas comuns</div><h1 class='sec'>Perguntas frequentes</h1>{fq}</div>")
    # Plano + checklist
    rows = "".join(f"<tr><th style='width:60pt'>{E(d)}</th><td>{E(a)}</td></tr>" for d, a in s["plano7"])
    cl = "".join(f"<li>{E(x)}</li>" for x in s["checklist_final"])
    out.append(f"<div class='page'><div class='kicker'>Mão na massa</div><h1 class='sec'>Seu plano de 7 dias</h1><table>{rows}</table><h2>Checklist final</h2><div class='cl'><ul>{cl}</ul></div></div>")
    # Ferramentas que eu uso
    tc = "".join(f"<div class='toolcard'><div class='tn'>{E(n)}</div><div class='td'>{E(d)}<div class='tl'><a href='{E(u)}'>{E(u.replace('https://',''))}</a></div></div></div>" for n, d, u in FERRAMENTAS)
    out.append(f"<div class='page'><div class='kicker'>Kit de ferramentas</div><h1 class='sec'>As ferramentas que eu uso</h1><p>São as ferramentas que uso no dia a dia do Isso É Dica. Algumas têm plano grátis para começar.</p>{tc}<p class='small'>Transparência: alguns links acima são de parceiro. Se você assinar por eles, eu recebo uma comissão, sem nenhum custo extra para você. Só indico o que uso.</p></div>")
    # Próximos passos (máquina de vendas)
    out.append(f"""<div class='page'><div class='kicker'>Próximos passos</div><h1 class='sec'>Quer ir mais longe?</h1>
<div class='cta'><h3>📚 Clube Isso É Dica</h3><p>Um guia novo como este toda semana, a biblioteca completa da coleção e os modelos prontos, com cancelamento quando quiser.</p><span class='btn'>Assinar o Clube</span><p style='margin-top:8pt'>{link_or_kw(L['clube'],'CLUBE')}</p></div>
<div class='next'><div class='tag'>GUIA</div><h3>Método Invisível</h3><p>Cresça e venda no Instagram sem precisar aparecer.</p>{link_or_kw(L['metodo'],'METODO')}</div>
<div class='next'><div class='tag'>GUIA</div><h3>IA no Negócio</h3><p>O passo a passo para usar IA para vender mais e trabalhar menos no seu negócio.</p>{link_or_kw(L['negocio'],'NEGOCIO')}</div>
<div class='next'><div class='tag'>INDIVIDUAL</div><h3>Sessão Raio-X e Mentoria de IA</h3><p>Eu olho o seu caso e a gente encontra onde a IA te dá tempo ou dinheiro. Você sai com o plano de ação.</p><a href='{E(L['mentoria'])}'>{E(L['mentoria'].replace('https://',''))}</a></div>
<div class='next'><div class='tag'>GRÁTIS</div><h3>Grupo VIP no WhatsApp</h3><p>Uma ferramenta de IA nova por dia, com o passo a passo.</p><a href='{E(L['grupo'])}'>{E(L['grupo'].replace('https://',''))}</a></div>
<div class='next'><div class='tag'>GANHE INDICANDO</div><h3>Seja afiliado deste guia</h3><p>Gostou? Indique para quem precisa e ganhe 50% de comissão em cada venda.</p>{link_or_kw(L['afiliacao'],'AFILIADO')}</div>
<p class='small'>Instagram <a href='{E(L['instagram'])}'>@issoedica</a> · YouTube <a href='{E(L['youtube'])}'>@issoedica</a></p>
<div class='legal'>© {E(s['mesano'].split('/')[-1])} Isso É Dica. Todos os direitos reservados. É proibido copiar, revender ou distribuir este material sem autorização. Os exemplos são ilustrativos e os resultados dependem da aplicação de cada pessoa. Ferramentas e preços citados podem mudar.</div></div>""")
    footer = "<div style='width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#8a8fa8;padding:0 18mm;display:flex;justify-content:space-between'><span>ISSO É DICA · " + E(s['titulo']) + "</span><span class='pageNumber'></span></div>"
    return f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{CSS}</style></head><body>{''.join(out)}</body></html>", footer


async def render(spec_path, outdir, links_path=None):
    from playwright.async_api import async_playwright
    s = json.load(open(spec_path, encoding="utf-8"))
    L = dict(DEFAULT_LINKS)
    if links_path and os.path.exists(links_path):
        L.update({k: v for k, v in json.load(open(links_path, encoding="utf-8")).items() if v})
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    slug = s["slug"]
    chtml = cover_html(s); bhtml, footer = body_html(s, L)
    (out / f"{slug}-capa.html").write_text(chtml, encoding="utf-8")
    (out / f"{slug}-miolo.html").write_text(bhtml, encoding="utf-8")
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page()
        await pg.set_content(chtml, wait_until="networkidle")
        await pg.pdf(path=str(out / "_capa.pdf"), format="A4", print_background=True)
        # PNGs da capa
        await pg.set_viewport_size({"width": 794, "height": 1123})
        await pg.screenshot(path=str(out / f"{slug}-capa-a4.png"), full_page=False, scale="device")
        pg2 = await br.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2.28)
        await pg2.set_content(chtml, wait_until="networkidle")
        await pg2.screenshot(path=str(out / "_capa_hi.png"))
        pg3 = await br.new_page()
        await pg3.set_content(bhtml, wait_until="networkidle")
        await pg3.pdf(path=str(out / "_miolo.pdf"), format="A4", print_background=True,
                      display_header_footer=True, header_template="<div></div>", footer_template=footer,
                      margin={"top": "20mm", "bottom": "18mm", "left": "18mm", "right": "18mm"})
        await br.close()
    w = PdfWriter()
    for f in ("_capa.pdf", "_miolo.pdf"):
        for pgx in PdfReader(str(out / f)).pages:
            w.add_page(pgx)
    w.add_metadata({"/Title": s["titulo"], "/Author": "Isso É Dica"})
    pdf = out / f"{slug}.pdf"
    with open(pdf, "wb") as fh:
        w.write(fh)
    # capas derivadas
    from PIL import Image, ImageFilter
    hi = Image.open(out / "_capa_hi.png").convert("RGB")
    vert = hi.resize((1600, int(1600 * hi.height / hi.width)))
    vert = vert.crop((0, 0, 1600, min(vert.height, 2560))) if vert.height >= 2560 else vert
    canvas = Image.new("RGB", (1600, 2560), (11, 16, 48)); canvas.paste(vert.resize((1600, 2263)) if vert.height < 2560 else vert, (0, 0))
    if vert.height < 2560:
        canvas = hi.resize((1810, 2560)).crop((105, 0, 1705, 2560))
    canvas.save(out / f"{slug}-capa-vertical.jpg", quality=92)
    # quadrada 1200x1200: fundo desfocado + capa em pé com sombra
    bg = hi.resize((1200, int(1200 * hi.height / hi.width))).crop((0, 300, 1200, 1500)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (11, 16, 48)), 0.35)
    bk = hi.resize((700, int(700 * hi.height / hi.width)))
    sh = Image.new("RGBA", (bk.width + 80, bk.height + 80), (0, 0, 0, 0))
    from PIL import ImageDraw
    ImageDraw.Draw(sh).rectangle([40, 50, bk.width + 40, bk.height + 50], fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    x, y = (1200 - bk.width) // 2, (1200 - bk.height) // 2
    bg.paste(sh, (x - 40, y - 30), sh); bg.paste(bk, (x, y))
    bg.save(out / f"{slug}-capa-quadrada.jpg", quality=92)
    for f in ("_capa.pdf", "_miolo.pdf", "_capa_hi.png"):
        (out / f).unlink(missing_ok=True)
    n = len(PdfReader(str(pdf)).pages)
    print(json.dumps({"pdf": str(pdf), "paginas": n}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
