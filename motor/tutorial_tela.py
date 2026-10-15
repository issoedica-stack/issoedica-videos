"""Motor de video tutorial de tela (faceless) do @issoedica.

Uso: python3 tutorial_tela.py roteiro.json pasta_imagens saida.mp4

O roteiro descreve cenas feitas com capturas REAIS da ferramenta (Chrome).
Efeitos: cold open com o resultado, camera guiada (zoom/pan), tremor de mao,
transicao whip com borrao, destaque que se desenha, toque no botao, legenda
palavra por palavra, gancho animado, CTA com palavra-chave, barra de
progresso e trilha de efeitos sonoros. Musica entra no app na hora de postar.
"""
import json, math, os, random, subprocess, sys, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
YEL = (255, 212, 0)
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
if not os.path.exists(FB):
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TR = 0.28          # duracao da transicao
SCREEN_Y = 1010    # centro vertical da tela capturada

R = json.load(open(sys.argv[1]))
IMG_DIR = sys.argv[2]
OUT_MP4 = sys.argv[3]
FR_DIR = OUT_MP4 + "_frames"
shutil.rmtree(FR_DIR, ignore_errors=True)
os.makedirs(FR_DIR)

FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
_font_cache = {}
def font(s, mono=False):
    k = (s, mono)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(FM if mono else FB, s)
    return _font_cache[k]

# fundo dos blocos de motion graphics: grade sutil + brilho roxo
MBG = Image.new("RGB", (W, H), (8, 9, 14)); _d = ImageDraw.Draw(MBG)
for _x in range(0, W, 60): _d.line([(_x, 0), (_x, H)], fill=(16, 18, 26))
for _y in range(0, H, 60): _d.line([(0, _y), (W, _y)], fill=(16, 18, 26))
_g = Image.new("L", (W, H), 0); ImageDraw.Draw(_g).ellipse([W/2-520, 500, W/2+520, 1500], fill=70)
MBG = Image.composite(Image.new("RGB", (W, H), (40, 30, 90)), MBG, _g.filter(ImageFilter.GaussianBlur(200))).convert("RGBA")
MUT = (120, 126, 150); CY = (0, 224, 198); RED = (255, 70, 70)

def eout(p):
    p = min(max(p, 0), 1); return 1 - (1 - p) ** 3
def seg(t, a, b): return min(max((t - a) / (b - a), 0), 1)

def scaled_text(canvas, txt, cy, size, fill, k, a=1.0):
    if k <= 0.01 or a <= 0: return
    f = font(size); tmp = Image.new("RGBA", (W, int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    w = d.textlength(txt, font=f); d.text(((W - w) / 2, size * 0.2), txt, font=f, fill=tuple(fill) + (int(255 * a),))
    sz = (max(1, int(tmp.width * k)), max(1, int(tmp.height * k)))
    canvas.alpha_composite(tmp.resize(sz, Image.BICUBIC), (int(W / 2 - sz[0] / 2), int(cy - sz[1] / 2)))

def motion_kinetic(s, lt):
    """Frases que entram com impacto (slam). lines: [texto, t0, cor, tamanho, (riscar)]"""
    c = MBG.copy(); d = ImageDraw.Draw(c)
    n = len(s["lines"]); y0 = 960 - (n - 1) * 90
    for i, ln in enumerate(s["lines"]):
        txt, t0, col, sz = ln[0], ln[1], tuple(ln[2]), ln[3]
        p = seg(lt, t0, t0 + 0.22)
        if p <= 0: continue
        out = seg(lt, s["d"] - 0.3, s["d"])
        scaled_text(c, txt, y0 + i * 180, sz, col, (1.6 - 0.6 * eout(p)) * (1 - 0.3 * out), a=p * (1 - out))
        if len(ln) > 4 and ln[4]:
            q = seg(lt, t0 + 0.4, t0 + 0.7)
            if q > 0:
                w = d.textlength(txt, font=font(sz))
                d.line([(W/2 - w/2 - 20, y0 + i*180), (W/2 - w/2 - 20 + (w + 40) * eout(q), y0 + i*180)], fill=RED + (int(255*(1-out)),), width=14)
    return c

def motion_prompt(s, lt):
    """Terminal com o prompt sendo digitado."""
    c = MBG.copy(); d = ImageDraw.Draw(c)
    p = seg(lt, 0, 0.3); out = seg(lt, s["d"] - 0.25, s["d"]); A = p * (1 - out)
    x0, y0, x1, y1 = 70, 560 + int(60 * (1 - eout(p))), W - 70, 1380
    d.rounded_rectangle([x0, y0, x1, y1], 30, fill=(14, 16, 24, int(245*A)), outline=(60, 64, 90, int(255*A)), width=3)
    for j, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([x0 + 36 + j*40, y0 + 34, x0 + 60 + j*40, y0 + 58], fill=col + (int(255*A),))
    d.text((x0 + 170, y0 + 30), s.get("app", "prompt"), font=font(30, True), fill=MUT + (int(255*A),))
    txt = s["text"]; per = (s["d"] * 0.7) / len(txt)
    n = int(max(0, lt - 0.35) / per); shown = txt[:min(n, len(txt))]
    lines, cur, f = [], "", font(42, True)
    for w in shown.split(" "):
        tst = (cur + " " + w).strip()
        if d.textlength(tst, font=f) <= x1 - x0 - 100: cur = tst
        else: lines.append(cur); cur = w
    lines.append(cur)
    for i, ln in enumerate(lines):
        d.text((x0 + 50, y0 + 120 + i * 62), ln, font=f, fill=CY + (int(255*A),))
    if n <= len(txt) and int(lt * 3) % 2 == 0:
        lx = x0 + 50 + d.textlength(lines[-1], font=f)
        d.text((lx, y0 + 120 + (len(lines)-1) * 62), "_", font=f, fill=CY + (int(255*A),))
    if s.get("tap") and lt > s["d"] * 0.82:
        q = seg(lt, s["d"] * 0.82, s["d"])
        bx, by = x1 - 120, y1 - 100
        d.rounded_rectangle([bx - 70, by - 40, bx + 70, by + 40], 40, fill=YEL + (int(255*A),))
        d.text((bx - 40, by - 26), "OK", font=font(44), fill=(10, 10, 10, int(255*A)))
        r = 30 + 50 * q
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=(255, 255, 255, int(255*(1-q))), width=7)
    return c

def motion_compare(s, lt):
    c = MBG.copy(); d = ImageDraw.Draw(c)
    out = seg(lt, s["d"] - 0.3, s["d"]); A = 1 - out
    p1 = seg(lt, 0.1, 0.35)
    if p1 > 0:
        f = font(56); w0 = d.textlength(s["a_label"], font=f); d.text((W/2 - w0/2, 600), s["a_label"], font=f, fill=MUT + (int(255*p1*A),))
        f = font(140); w = d.textlength(s["a"], font=f); d.text((W/2 - w/2, 680), s["a"], font=f, fill=(245, 246, 250, int(255*p1*A)))
        q = seg(lt, 0.6, 0.9)
        if q > 0: d.line([(W/2 - w/2 - 20, 785), (W/2 - w/2 - 20 + (w + 40) * eout(q), 785)], fill=RED + (int(255*A),), width=16)
    p2 = seg(lt, 1.2, 1.45)
    if p2 > 0:
        f = font(56); w0 = d.textlength(s["b_label"], font=f); d.text((W/2 - w0/2, 1000), s["b_label"], font=f, fill=MUT + (int(255*p2*A),))
        scaled_text(c, s["b"], 1160, 140, YEL, back(p2), a=A)
    return c

def ease(p):
    p = min(max(p, 0), 1)
    return p * p * (3 - 2 * p)

def back(p):
    c = 1.7; p -= 1
    return 1 + (c + 1) * p ** 3 + c * p ** 2

# ---------- carregar imagens (com borroes de privacidade) ----------
_img_cache, _bg_cache = {}, {}
def load(name, blurs):
    key = (name, json.dumps(blurs))
    if key not in _img_cache:
        im = Image.open(os.path.join(IMG_DIR, name)).convert("RGB")
        for b in blurs or []:
            b = tuple(int(v) for v in b)
            im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(12)), b[:2])
        _img_cache[key] = im
    return _img_cache[key]

def background(img):
    k = id(img)
    if k not in _bg_cache:
        bg = img.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(10)).resize((W, H))
        _bg_cache[k] = ImageEnhance.Brightness(bg).enhance(0.30).convert("RGBA")
    return _bg_cache[k].copy()

SC = R["scenes"]
starts, t = [], 0.0
for s in SC:
    starts.append(t); t += s["d"]
TOTAL = t

# ---------- camada da tela ----------
def screen_layer(s, lt, gt):
    kind = s.get("type")
    if kind == "kinetic": return motion_kinetic(s, lt)
    if kind == "prompt": return motion_prompt(s, lt)
    if kind == "compare": return motion_compare(s, lt)
    if kind == "cta": return MBG.copy()
    p = min(max(lt / s["d"], 0), 1)
    imgs = [load(n, s.get("blur")) for n in s["imgs"]]
    img = imgs[min(int(p * len(imgs) * 1.15), len(imgs) - 1)]
    e = ease(p)
    b0, b1 = s["b0"], s.get("b1", s["b0"])
    b = [b0[i] + (b1[i] - b0[i]) * e for i in range(4)]
    sc = 1000 / (b[2] - b[0])
    canvas = background(img)
    fw, fh = int(img.width * sc), int(img.height * sc)
    fg = img.resize((fw, fh), Image.BICUBIC)
    if s.get("dim"):
        fg = ImageEnhance.Brightness(fg.filter(ImageFilter.GaussianBlur(16))).enhance(0.5)
    dx = 5 * math.sin(gt * 2.1) + 2 * math.sin(gt * 5.3)
    dy = 5 * math.cos(gt * 1.8) + 2 * math.sin(gt * 4.7)
    ox = W / 2 - (b[0] + b[2]) / 2 * sc + dx
    oy = SCREEN_Y - (b[1] + b[3]) / 2 * sc + dy
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(fg.convert("RGBA"), (int(ox), int(oy)))
    if s.get("hl") and lt > 0.35:
        q = min((lt - 0.35) / 0.55, 1)
        x0, y0, x1, y1 = s["hl"]
        X0, Y0, X1, Y1 = ox + x0 * sc, oy + y0 * sc, ox + x1 * sc, oy + y1 * sc
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.rectangle([X0, Y0, X1, Y1], fill=YEL + (int(38 * q),))
        pts = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1), (X0, Y0)]
        dist = 2 * ((X1 - X0) + (Y1 - Y0)) * ease(q); acc = 0
        for i in range(4):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            seg = math.hypot(bx - ax, by - ay)
            if acc < dist:
                f = min((dist - acc) / seg, 1)
                d.line([(ax, ay), (ax + (bx - ax) * f, ay + (by - ay) * f)], fill=YEL + (255,), width=9)
            acc += seg
        layer.alpha_composite(ov.filter(ImageFilter.GaussianBlur(8))); layer.alpha_composite(ov)
    if s.get("tap") and p > 0.8:
        q = (p - 0.8) / 0.2
        tx, ty = ox + s["tap"][0] * sc, oy + s["tap"][1] * sc
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        r = 26 + 50 * q
        d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 255, 255, int(255 * (1 - q))), width=7)
        d.ellipse([tx - 22, ty - 22, tx + 22, ty + 22], fill=(255, 255, 255, int(170 * (1 - q))))
        layer.alpha_composite(ov)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([ox + 20, oy + 30, ox + fw + 20, oy + fh + 30], fill=(0, 0, 0, 150))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    ang = -0.9 + 0.3 * math.sin(gt * 1.6)
    canvas.alpha_composite(layer.rotate(ang, resample=Image.BICUBIC, center=(W / 2, SCREEN_Y)))
    return canvas

# ---------- textos ----------
def stamp(canvas, txt, lt):
    a = min(lt / 0.2, 1); k = back(a) if a < 1 else 1
    f = font(70); tmp = Image.new("RGBA", (700, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle([(700 - tw) / 2 - 40, 20, (700 + tw) / 2 + 40, 140], 30, fill=YEL + (255,))
    d.text(((700 - tw) / 2, 32), txt, font=f, fill=(10, 10, 10))
    tmp = tmp.rotate(-4, resample=Image.BICUBIC, expand=True)
    sz = (max(1, int(tmp.width * k)), max(1, int(tmp.height * k)))
    tmp = tmp.resize(sz)
    canvas.alpha_composite(tmp, (int(W / 2 - sz[0] / 2), int(1560 - sz[1] / 2)))

def caption_words(canvas, s, lt):
    """Legenda palavra por palavra (estilo karaoke) dentro de um cartao."""
    words = s["cap"].split()
    sub = s.get("sub")
    per = min(0.16, max(0.08, (s["d"] - TR - 0.6) / max(len(words), 1)))
    shown = int(lt / per) + 1
    f1, f2 = font(64), font(50)
    tmp = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    full = " ".join(words)
    w1 = d.textlength(full, font=f1); w2 = d.textlength(sub, font=f2) if sub else 0
    bw, bh = max(w1, w2) + 80, 110 + (70 if sub else 0)
    x0 = (W - bw) / 2
    a = min(lt / 0.2, 1); k = back(a) if a < 1 else 1
    d.rounded_rectangle([x0, 10, x0 + bw, 10 + bh], 30, fill=(12, 12, 12, 228))
    d.rounded_rectangle([x0, 10, x0 + 14, 10 + bh], 7, fill=YEL + (255,))
    x = (W - w1) / 2
    for i, w in enumerate(words):
        if i < shown:
            col = YEL if i == shown - 1 and shown <= len(words) else (255, 255, 255)
            d.text((x, 30), w, font=f1, fill=col)
        x += d.textlength(w + " ", font=f1)
    if sub and shown > len(words):
        d.text(((W - w2) / 2, 112), sub, font=f2, fill=YEL)
    sz = (max(1, int(W * k)), max(1, int(300 * k)))
    tmp = tmp.resize(sz, Image.BICUBIC)
    canvas.alpha_composite(tmp, (int((W - sz[0]) / 2), int(1590 + (300 - sz[1]) / 2)))

def hook(canvas, gt):
    lines = R["hook"]; hl = set(R.get("hook_hl", []))
    f = font(70); lh = 90; y = 150
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    bw = max(d.textlength(" ".join(l), font=f) for l in lines)
    x0 = (W - bw - 80) / 2
    d.rounded_rectangle([x0, y - 25, x0 + bw + 80, y - 25 + lh * len(lines) + 45], 32,
                        fill=(0, 0, 0, int(215 * min(gt / 0.2, 1))))
    idx = 0
    for li, ln in enumerate(lines):
        x = (W - d.textlength(" ".join(ln), font=f)) / 2
        for w in ln:
            ap = min(max((gt - 0.1 * idx) / 0.22, 0), 1)
            if ap > 0:
                col = YEL if w in hl else (255, 255, 255)
                d.text((x, y + li * lh + int(22 * (1 - ease(ap)))), w, font=f, fill=col + (int(255 * ap),))
            x += d.textlength(w + " ", font=f); idx += 1
    canvas.alpha_composite(ov)

def cta(canvas, lt):
    c = R["cta"]
    a = min(lt / 0.3, 1); k = back(a) if a < 1 else 1 + 0.03 * math.sin(lt * 6)
    tmp = Image.new("RGBA", (W, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    f1, f2, f3 = font(64), font(120), font(56)
    d.text(((W - d.textlength(c["pre"], font=f1)) / 2, 30), c["pre"], font=f1, fill="white")
    kw = c["kw"]; kwid = d.textlength(kw, font=f2)
    d.rounded_rectangle([(W - kwid) / 2 - 40, 120, (W + kwid) / 2 + 40, 290], 34, fill=YEL + (255,))
    d.text(((W - kwid) / 2, 128), kw, font=f2, fill=(10, 10, 10))
    yy = 330
    for ln in c["pos"].split("\n"):
        d.text(((W - d.textlength(ln, font=f3)) / 2, yy), ln, font=f3, fill="white"); yy += 72
    ay = yy + 30 + 18 * abs(math.sin(lt * 5))
    d.polygon([(W / 2 - 45, ay), (W / 2 + 45, ay), (W / 2, ay + 60)], fill=YEL + (255,))
    sz = (int(W * k), int(640 * k))
    tmp = tmp.resize(sz, Image.BICUBIC)
    canvas.alpha_composite(tmp, (int((W - sz[0]) / 2), int(760 + (640 - sz[1]) / 2)))

def chrome(canvas, gt):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, int(W * gt / TOTAL), 9], fill=YEL)
    d.text((W - 260, 1862), R.get("handle", "@issoedica"), font=font(34), fill=(255, 255, 255, 150))

def scene_frame(si, lt, gt):
    s = SC[si]
    c = screen_layer(s, lt, gt)
    tr = TR if si > 0 else 0
    if lt > tr:
        if s.get("stamp"):
            stamp(c, s["stamp"], lt - tr)
        elif s.get("cta") or s.get("type") == "cta":
            cta(c, lt - tr)
        elif s.get("cap"):
            caption_words(c, s, lt - tr)
    return c

def whip(a, b, q):
    off = int(W * ease(q))
    out = Image.new("RGBA", (W, H)); out.paste(a, (-off, 0)); out.paste(b, (W - off, 0))
    k = math.sin(math.pi * q)
    if k > 0.05:
        arr = np.asarray(out, np.float32); acc = np.zeros_like(arr)
        for i in range(7):
            acc += np.roll(arr, int((i - 3) * 22 * k), axis=1)
        out = Image.fromarray((acc / 7).astype(np.uint8), "RGBA")
    return out

# ---------- render ----------
sfx = []
THUMPS = []
for i, s_ in enumerate(SC):
    if s_.get("type") == "kinetic":
        THUMPS += [starts[i] + ln[1] for ln in s_["lines"]]
    if s_.get("type") == "cta": THUMPS.append(starts[i] + TR + 0.35)
nf = int(TOTAL * FPS)
for fi in range(nf):
    gt = fi / FPS
    si = max(i for i in range(len(SC)) if starts[i] <= gt + 1e-9)
    lt = gt - starts[si]; s = SC[si]
    base = scene_frame(si, lt, gt)
    if si > 0 and lt < TR:
        base = whip(scene_frame(si - 1, SC[si - 1]["d"] + lt, gt), base, lt / TR)
    if s.get("flash") and lt < 0.15:
        base.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - lt / 0.15)))))
    if not s.get("cta") and s.get("type") not in ("kinetic", "compare", "cta") and not s.get("nohook"):
        hook(base, gt)
    chrome(base, gt)
    sh = max([max(0, 1 - (gt - x) / 0.25) for x in THUMPS if gt >= x] + [0])
    if sh > 0:
        arr = np.asarray(base)
        base = Image.fromarray(np.roll(np.roll(arr, int(random.uniform(-18, 18) * sh), 1), int(random.uniform(-18, 18) * sh), 0))
    base.convert("RGB").save(f"{FR_DIR}/{fi:05d}.jpg", quality=92)

# ---------- efeitos sonoros ----------
rng = np.random.default_rng(1); random.seed(1)
for i, s in enumerate(SC):
    st = starts[i]
    if i > 0: sfx.append((st, "whoosh"))
    if s.get("cap") or s.get("cta") or s.get("stamp"): sfx.append((st + (TR if i else 0), "pop"))
    if len(s.get("imgs", [])) > 1:
        tt = st + 0.3
        while tt < st + s["d"] * 0.78:
            sfx.append((tt, "key")); tt += random.uniform(0.07, 0.15)
    if s.get("tap"): sfx.append((st + s["d"] * 0.8, "click"))
    if s.get("hl"): sfx.append((st + 0.35, "swipe"))
    if s.get("type") == "kinetic":
        for ln in s["lines"]:
            sfx.append((st + ln[1], "thump"))
            if len(ln) > 4 and ln[4]: sfx.append((st + ln[1] + 0.4, "swipe"))
    if s.get("type") == "prompt":
        tt = st + 0.35; end = st + 0.35 + s["d"] * 0.7
        while tt < end: sfx.append((tt, "key")); tt += random.uniform(0.05, 0.11)
        if s.get("tap"): sfx.append((st + s["d"] * 0.82, "click"))
    if s.get("type") == "compare": sfx += [(st + 0.1, "thump"), (st + 1.2, "thump")]
    if s.get("type") == "cta": sfx.append((st + TR + 0.35, "thump"))
    if s.get("ding"): sfx.append((st + s["ding"], "ding"))
sr = 44100
track = np.zeros(int((TOTAL + 1) * sr), np.float32)
def add(t0, sig):
    i = max(int(t0 * sr), 0); track[i:i + len(sig)] += sig[: len(track) - i]
for t0, kind in sfx:
    if kind == "whoosh":
        x = np.linspace(0, 1, int(0.45 * sr)); n = rng.normal(0, 1, len(x))
        sm = np.convolve(n, np.ones(18) / 18, "same") - np.convolve(n, np.ones(120) / 120, "same")
        add(t0 - 0.12, 0.55 * sm * np.sin(np.pi * x) ** 2)
    elif kind == "pop":
        x = np.linspace(0, 0.12, int(0.12 * sr)); f = 900 - 500 * x / 0.12
        add(t0, 0.35 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-x * 35))
    elif kind == "key":
        x = np.linspace(0, 0.03, int(0.03 * sr)); add(t0, 0.18 * rng.normal(0, 1, len(x)) * np.exp(-x * 220))
    elif kind == "click":
        x = np.linspace(0, 0.06, int(0.06 * sr)); add(t0, 0.4 * np.sin(2 * np.pi * 1800 * x) * np.exp(-x * 90))
    elif kind == "thump":
        x = np.linspace(0, 0.35, int(0.35 * sr)); f = 110 * np.exp(-x * 9) + 45
        add(t0, 0.8 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-x * 9) + 0.22 * rng.normal(0, 1, len(x)) * np.exp(-x * 60))
    elif kind == "ding":
        x = np.linspace(0, 0.8, int(0.8 * sr)); add(t0, 0.3 * (np.sin(2 * np.pi * 1320 * x) + 0.5 * np.sin(2 * np.pi * 1980 * x)) * np.exp(-x * 5))
    elif kind == "swipe":
        x = np.linspace(0, 1, int(0.3 * sr)); add(t0, 0.12 * np.sin(2 * np.pi * np.cumsum(400 + 900 * x) / sr) * np.sin(np.pi * x))
wav = OUT_MP4 + ".sfx.wav"
with wave.open(wav, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{FR_DIR}/%05d.jpg", "-i", wav,
                "-filter_complex", "[0:v]noise=alls=5:allf=t,vignette=PI/6,format=yuv420p[v]",
                "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "21", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT_MP4], check=True)
shutil.rmtree(FR_DIR, ignore_errors=True); os.remove(wav)
print("VIDEO_OK", OUT_MP4, round(TOTAL, 1), "s")
