#!/usr/bin/env python3
"""Motor de video @issoedica: roteiro.json -> video.mp4 (1080x1920, 30fps, motion graphics).
Uso: python3 render.py roteiro.json saida.mp4 [pasta_fontes]
roteiro.json: {"tag":"NOVIDADE DE IA","hook":"Titulo com *destaque*","sub":"linha de apoio",
 "pontos":[{"titulo":"...","texto":"..."}, x3], "cta":"Comenta IA", "cta_sub":"..."}
"""
import json, sys, os, subprocess, base64, html, re
from playwright.sync_api import sync_playwright

W, H, FPS = 1080, 1920, 30
rot = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = sys.argv[2]
FONTS = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

def font_face(w):
    p = os.path.join(FONTS, f"montserrat-latin-{w}-normal.woff2")
    b = base64.b64encode(open(p, "rb").read()).decode()
    return f"@font-face{{font-family:M;font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2')}}"

def words(txt, base_delay, step=0.09, cls="w"):
    out, i, hl = [], 0, False
    for tok in txt.strip().split():
        start = tok.startswith("*")
        if start: hl = True
        cur = hl
        if tok.rstrip(".,!?:;").endswith("*"): hl = False
        t = html.escape(tok.replace("*", ""))
        d = base_delay + i * step
        out.append(f'<span class="{cls}{" hl" if cur else ""}" style="--d:{d:.2f}s"><i>{t}</i></span>')
        i += 1
    return " ".join(out), base_delay + i * step

pontos = rot["pontos"][:3]
narr = rot.get("narracao") or {}
def _dur(txt, base):
    w = len(str(txt or "").split())
    return round(min(8.5, max(base, w / 2.5 + 0.9)), 2) if w else base
N_HOOK = narr.get("hook", ""); N_PTS = (narr.get("pontos") or ["", "", ""])[:3]; N_CTA = narr.get("cta", "")
D_HOOK = _dur(N_HOOK, 4.6); D_CTA = _dur(N_CTA, 4.4)
D_PTS = [_dur(N_PTS[i] if i < len(N_PTS) else "", 5.2) for i in range(len(pontos))]
scenes, t = [], 0.0

# Cena 1: gancho
hk, _ = words(rot["hook"], t + 0.35, 0.10)
scenes.append((t, D_HOOK, f'''
 <div class="tag" style="--d:{t+0.1:.2f}s"><b></b>{html.escape(rot.get("tag","NOVIDADE DE IA"))}</div>
 <h1 class="hook">{hk}</h1>
 <p class="sub fade" style="--d:{t+1.6:.2f}s">{html.escape(rot.get("sub",""))}</p>
 <div class="bar" style="--d:{t+1.3:.2f}s"></div>'''))
t += D_HOOK
# Cenas 2-4: pontos
for n, p in enumerate(pontos, 1):
    tt, _ = words(p["titulo"], t + 0.45, 0.08)
    D_PT = D_PTS[n - 1]
    scenes.append((t, D_PT, f'''
 <div class="num" style="--d:{t+0.05:.2f}s">0{n}</div>
 <div class="ring" style="--d:{t+0.1:.2f}s"></div>
 <h2 class="pt">{tt}</h2>
 <div class="line" style="--d:{t+0.9:.2f}s"></div>
 <p class="txt fade" style="--d:{t+1.1:.2f}s">{html.escape(p["texto"])}</p>'''))
    t += D_PT
# Cena final: CTA
ct, _ = words(rot.get("cta_titulo", "Quer mais dicas assim?"), t + 0.3, 0.08)
scenes.append((t, D_CTA, f'''
 <h2 class="pt c">{ct}</h2>
 <div class="btn" style="--d:{t+1.0:.2f}s">{html.escape(rot.get("cta","Comenta IA"))}</div>
 <p class="txt fade c" style="--d:{t+1.5:.2f}s">{html.escape(rot.get("cta_sub","e receba o link no direct"))}</p>
 <div class="handle fade" style="--d:{t+1.9:.2f}s">@issoedica</div>'''))
t += D_CTA
TOTAL = t

scene_html = "".join(
    f'<section class="sc" style="--s:{s:.2f}s;--len:{d:.2f}s">{body}</section>' for s, d, body in scenes)

CSS = "".join(font_face(w) for w in (400, 600, 800, 900)) + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#000;font-family:M;color:#fff}}
:root{{--c:#00CCFF}}
#bg{{position:absolute;inset:0;overflow:hidden}}
.grid{{position:absolute;inset:-200px;background-image:linear-gradient(rgba(0,204,255,.07) 2px,transparent 2px),linear-gradient(90deg,rgba(0,204,255,.07) 2px,transparent 2px);background-size:90px 90px;transform:perspective(900px) rotateX(58deg) translateY(300px);animation:gridmove {TOTAL}s linear forwards}}
@keyframes gridmove{{to{{background-position:0 {int(TOTAL*60)}px}}}}
.orb{{position:absolute;border-radius:50%;filter:blur(90px);opacity:.55}}
.o1{{width:720px;height:720px;background:#00CCFF;left:-260px;top:-200px;animation:f1 {TOTAL}s ease-in-out forwards}}
.o2{{width:620px;height:620px;background:#2a3cff;right:-240px;bottom:120px;opacity:.35;animation:f2 {TOTAL}s ease-in-out forwards}}
@keyframes f1{{50%{{transform:translate(260px,380px) scale(1.2)}}100%{{transform:translate(80px,900px) scale(.9)}}}}
@keyframes f2{{50%{{transform:translate(-300px,-500px) scale(1.15)}}100%{{transform:translate(-60px,-1000px)}}}}
.vig{{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 45%,rgba(0,0,0,.85) 100%)}}
.scan{{position:absolute;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,rgba(0,204,255,.5),transparent);animation:scan 3.2s linear infinite}}
@keyframes scan{{from{{top:-10px}}to{{top:{H}px}}}}
#top{{position:absolute;top:90px;left:80px;right:80px;display:flex;align-items:center;justify-content:space-between;z-index:5}}
.chip{{font-weight:800;font-size:30px;letter-spacing:4px;padding:14px 26px;border:2px solid var(--c);border-radius:40px;background:rgba(0,204,255,.08)}}
.chip span{{color:var(--c)}}
.live{{font-weight:600;font-size:26px;letter-spacing:3px;color:#9fb3c8;display:flex;align-items:center;gap:12px}}
.live b{{width:14px;height:14px;border-radius:50%;background:var(--c);box-shadow:0 0 18px var(--c);animation:pulse 1s ease-in-out infinite}}
#prog{{position:absolute;top:0;left:0;height:8px;background:var(--c);box-shadow:0 0 20px var(--c);width:100%;transform-origin:left;animation:prog {TOTAL}s linear forwards;z-index:6}}
@keyframes prog{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.sc{{position:absolute;left:80px;right:80px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;opacity:0;animation:scin var(--len) linear var(--s) forwards}}
@keyframes scin{{0%{{opacity:0;transform:scale(1.04);filter:blur(0)}}6%{{opacity:1;transform:scale(1);filter:blur(0)}}92%{{opacity:1;transform:scale(1) translateY(0);filter:blur(0)}}100%{{opacity:0;transform:scale(.97) translateY(-40px);filter:blur(8px)}}}}
.w{{display:inline-block;overflow:hidden;vertical-align:bottom;padding-bottom:6px}}
.w i{{display:inline-block;font-style:normal;transform:translateY(110%) rotate(6deg);animation:up .55s cubic-bezier(.2,.9,.25,1.2) var(--d) forwards}}
@keyframes up{{to{{transform:translateY(0) rotate(0)}}}}
.hl i{{color:var(--c);text-shadow:0 0 30px rgba(0,204,255,.6)}}
.hook{{font-weight:900;font-size:104px;line-height:1.02;letter-spacing:-2px;text-transform:uppercase}}
.pt{{font-weight:900;font-size:86px;line-height:1.05;letter-spacing:-1px;margin-top:10px}}
.tag{{align-self:flex-start;display:flex;align-items:center;gap:14px;font-weight:800;font-size:30px;letter-spacing:5px;color:#000;background:var(--c);padding:14px 24px;margin-bottom:46px;clip-path:inset(0 100% 0 0);animation:wipe .5s ease-out var(--d) forwards}}
.tag b{{width:12px;height:12px;background:#000;border-radius:50%}}
@keyframes wipe{{to{{clip-path:inset(0 0 0 0)}}}}
.fade{{opacity:0;transform:translateY(30px);animation:fd .6s ease-out var(--d) forwards}}
@keyframes fd{{to{{opacity:1;transform:none}}}}
.sub{{font-weight:600;font-size:44px;line-height:1.3;color:#b9c7d6;margin-top:40px}}
.txt{{font-weight:600;font-size:48px;line-height:1.32;color:#d3dde8;margin-top:34px}}
.bar{{width:220px;height:12px;background:var(--c);margin-top:44px;transform:scaleX(0);transform-origin:left;animation:grow .6s ease-out var(--d) forwards;box-shadow:0 0 24px var(--c)}}
.line{{width:100%;height:3px;background:linear-gradient(90deg,var(--c),transparent);margin-top:34px;transform:scaleX(0);transform-origin:left;animation:grow .8s ease-out var(--d) forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.num{{font-weight:900;font-size:300px;line-height:.9;color:transparent;-webkit-text-stroke:4px var(--c);opacity:0;transform:translateX(-80px);animation:numin .7s cubic-bezier(.2,.9,.25,1) var(--d) forwards}}
@keyframes numin{{to{{opacity:1;transform:none}}}}
.ring{{position:absolute;right:-40px;top:420px;width:300px;height:300px;border-radius:50%;border:6px solid var(--c);border-right-color:transparent;border-bottom-color:transparent;opacity:0;animation:ring 5s linear var(--d) forwards}}
@keyframes ring{{8%{{opacity:.8}}100%{{opacity:.8;transform:rotate(540deg)}}}}
.c{{text-align:center}}
.btn{{align-self:center;margin-top:60px;font-weight:900;font-size:72px;color:#000;background:var(--c);padding:34px 70px;border-radius:90px;box-shadow:0 0 60px rgba(0,204,255,.7);transform:scale(0);animation:pop .5s cubic-bezier(.3,1.6,.5,1) var(--d) forwards,pulse 0.9s ease-in-out calc(var(--d) + .6s) infinite}}
@keyframes pop{{to{{transform:scale(1)}}}}
@keyframes pulse{{50%{{transform:scale(1.07)}}}}
.handle{{text-align:center;margin-top:70px;font-weight:800;font-size:44px;letter-spacing:3px;color:var(--c)}}
"""

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="bg"><div class="grid"></div><div class="orb o1"></div><div class="orb o2"></div><div class="scan"></div><div class="vig"></div></div>
<div id="prog"></div>
<div id="top"><div class="chip">ISSO <span>É</span> DICA</div><div class="live"><b></b>IA HOJE</div></div>
{scene_html}
</body></html>"""

nframes = int(TOTAL * FPS)
tmp_v = OUT + ".v.mp4"
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                       "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
                       "-crf", "20", "-r", str(FPS), tmp_v], stdin=subprocess.PIPE)
with sync_playwright() as pw:
    br = pw.chromium.launch(args=["--disable-gpu"])
    pg = br.new_page(viewport={"width": W, "height": H})
    pg.set_content(HTML)
    pg.evaluate("document.fonts.ready")
    pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
    for f in range(nframes):
        pg.evaluate(f"(()=>{{const t={f*1000/FPS};document.getAnimations().forEach(a=>a.currentTime=t)}})()")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
    br.close()
ff.stdin.close(); ff.wait()

# Trilha propria (gerada por codigo) + ficha de cenas para a narracao (n8n)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trilha import gerar
cuts = [st for st, _, _ in scenes[1:]]
wav = OUT + ".wav"
gerar(TOTAL, cuts, wav, seed=abs(hash(rot.get("hook", ""))) % 1000)
alvo = "-20" if narr else "-15"  # com narracao a musica fica mais baixa
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_v, "-i", wav,
                "-af", f"loudnorm=I={alvo}:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-ar", "44100", "-shortest", "-movflags", "+faststart", OUT], check=True)
os.remove(wav)
textos = [N_HOOK] + [N_PTS[i] if i < len(N_PTS) else "" for i in range(len(pontos))] + [N_CTA]
ficha = {"duracao": round(TOTAL, 2), "cenas": [{"inicio": round(st, 2), "duracao": d, "narracao": textos[i]}
         for i, (st, d, _) in enumerate(scenes)]}
json.dump(ficha, open(OUT + ".cenas.json", "w"), ensure_ascii=False, indent=1)
os.remove(tmp_v)
print(json.dumps({"ok": True, "arquivo": OUT, "duracao_s": round(TOTAL, 1), "frames": nframes}))
