#!/usr/bin/env python3
"""Miniatura viral para o YouTube (padrão Isso É Dica, desde 18/11/2026).

Uso:
  python3 motor/miniatura_yt.py <hero.jpg> "<linha 1>" "<linha 2 em destaque>" <saida.jpg> \
      [--selo "CHATGPT"] [--formato short|longo] [--cor amarelo|ciano|verde|rosa]

- hero.jpg: imagem de fundo gerada no Gemini (Nano Banana), sem texto, com o terço superior escuro.
- linha 1: contexto curto em branco (2 a 4 palavras). linha 2: a promessa em destaque (1 a 3 palavras, GRANDE).
- --selo: nome da ferramenta numa pílula com glow (texto, nunca logo de terceiro).
- formato short = 1080x1920 (Shorts, padrão); longo = 1280x720.
Sai em JPG < 2 MB (limite do YouTube).
"""
import os, sys, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
F_BLACK = os.path.join(HERE, "fonts", "InterDisplay-Black.otf")
F_XB = os.path.join(HERE, "fonts", "InterDisplay-ExtraBold.otf")
CORES = {"amarelo": (255, 214, 0), "ciano": (0, 229, 255), "verde": (57, 255, 136), "rosa": (255, 64, 160)}


def cover(im, W, H, foco_y=0.55):
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * foco_y)
    return im.crop((x, y, x + W, y + H))


def fonte_que_cabe(texto, path, larg_max, tam_max, d):
    t = tam_max
    while t > 30:
        f = ImageFont.truetype(path, t)
        if d.textlength(texto, font=f) <= larg_max:
            return f
        t -= 4
    return ImageFont.truetype(path, t)


def texto_pop(base, xy, texto, fonte, cor, stroke, glow_cor=None, glow_raio=28, ancora="mm"):
    W, H = base.size
    if glow_cor:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).text(xy, texto, font=fonte, fill=glow_cor + (255,), anchor=ancora,
                               stroke_width=stroke * 2, stroke_fill=glow_cor + (255,))
        base.alpha_composite(g.filter(ImageFilter.GaussianBlur(glow_raio)))
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(s).text((xy[0] + stroke // 2, xy[1] + stroke), texto, font=fonte, fill=(0, 0, 0, 200),
                           anchor=ancora, stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    base.alpha_composite(s.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(base).text(xy, texto, font=fonte, fill=cor + (255,), anchor=ancora,
                              stroke_width=stroke, stroke_fill=(0, 0, 0, 255))


def pilula(base, cx, cy, texto, cor, tam):
    d = ImageDraw.Draw(base)
    f = ImageFont.truetype(F_XB, tam)
    tw = d.textlength(texto, font=f)
    pw, ph = tw + tam * 1.4, tam * 1.75
    box = [cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2]
    g = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle(box, radius=ph / 2, fill=cor + (200,))
    base.alpha_composite(g.filter(ImageFilter.GaussianBlur(tam * 0.7)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=ph / 2, fill=(8, 10, 20, 235), outline=cor + (255,), width=max(3, tam // 10))
    d.text((cx, cy), texto, font=f, fill=cor + (255,), anchor="mm")


def logo_recortada(lado):
    lg = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
    px = lg.load()
    for y in range(lg.height):
        for x in range(lg.width):
            r, g, b, a = px[x, y]
            if r < 45 and g < 50 and b < 62:
                px[x, y] = (r, g, b, 0)
    return lg.resize((lado, int(lado * lg.height / lg.width)), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero"); ap.add_argument("linha1"); ap.add_argument("linha2"); ap.add_argument("saida")
    ap.add_argument("--selo", default="")
    ap.add_argument("--formato", default="short", choices=["short", "longo"])
    ap.add_argument("--cor", default="amarelo", choices=list(CORES))
    a = ap.parse_args()
    W, H = (1080, 1920) if a.formato == "short" else (1280, 720)
    cor = CORES[a.cor]

    hero = Image.open(a.hero).convert("RGB")
    bg = cover(hero, W, H, 0.6 if a.formato == "short" else 0.55)
    bg = ImageEnhance.Contrast(bg).enhance(1.12)
    bg = ImageEnhance.Color(bg).enhance(1.15).convert("RGBA")

    # escurece o topo (área do texto) e uma vinheta nas bordas
    grad = Image.new("L", (1, H))
    topo = 0.50 if a.formato == "short" else 0.62
    for y in range(H):
        t = y / H
        grad.putpixel((0, y), int(225 * max(0.0, 1 - t / topo) ** 1.2))
    escuro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    escuro.putalpha(grad.resize((W, H)))
    bg.alpha_composite(escuro)
    vin = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vin).ellipse([-W * 0.25, -H * 0.15, W * 1.25, H * 1.15], fill=255)
    vin = Image.eval(vin.filter(ImageFilter.GaussianBlur(W // 6)), lambda v: 255 - v)
    vv = Image.new("RGBA", (W, H), (0, 0, 0, 255)); vv.putalpha(Image.eval(vin, lambda v: int(v * 0.75)))
    bg.alpha_composite(vv)

    d = ImageDraw.Draw(bg)
    margem = int(W * 0.07)
    larg = W - 2 * margem
    l1 = a.linha1.upper(); l2 = a.linha2.upper()

    if a.formato == "short":
        y_selo, y1 = 250, 430
        f1 = fonte_que_cabe(l1, F_BLACK, larg, 118, d)
        f2 = fonte_que_cabe(l2, F_BLACK, larg, 230, d)
        y2 = y1 + int(f1.size * 0.62) + int(f2.size * 0.62) + 10
        logo_lado, logo_pos = 170, (W - 170 - 34, H - 210)
        sel_tam = 50
    else:
        y_selo, y1 = 80, 205
        f1 = fonte_que_cabe(l1, F_BLACK, int(W * 0.9), 92, d)
        f2 = fonte_que_cabe(l2, F_BLACK, int(W * 0.9), 170, d)
        y2 = y1 + int(f1.size * 0.6) + int(f2.size * 0.6) + 6
        logo_lado, logo_pos = 120, (W - 120 - 24, H - 140)
        sel_tam = 36

    if a.selo:
        pilula(bg, W // 2, y_selo, a.selo.upper(), (0, 229, 255), sel_tam)
    texto_pop(bg, (W // 2, y1), l1, f1, (255, 255, 255), max(6, f1.size // 14))
    texto_pop(bg, (W // 2, y2), l2, f2, cor, max(8, f2.size // 13), glow_cor=cor, glow_raio=f2.size // 4)

    # sublinhado de energia sob o destaque
    tw = d.textlength(l2, font=f2)
    yb = y2 + int(f2.size * 0.62)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle([W / 2 - tw * 0.42, yb, W / 2 + tw * 0.42, yb + 14], radius=7, fill=cor + (255,))
    bg.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
    bg.alpha_composite(g)

    lg = logo_recortada(logo_lado)
    bg.alpha_composite(lg, logo_pos)

    out = bg.convert("RGB")
    q = 92
    out.save(a.saida, "JPEG", quality=q, optimize=True)
    while os.path.getsize(a.saida) > 1_900_000 and q > 60:
        q -= 6
        out.save(a.saida, "JPEG", quality=q, optimize=True)
    print("miniatura ok:", a.saida, out.size, os.path.getsize(a.saida), "bytes")


if __name__ == "__main__":
    main()
