#!/usr/bin/env python3
"""Capa padrao do @issoedica (Reels 9:16, 1080x1920).

Uso:
  python3 capa_gen.py "<titulo>" "<palavras em amarelo>" saida.jpg [selo]

- titulo: frase curta (ate ~7 palavras) com a promessa do video.
- palavras em amarelo: trecho do titulo que vai em destaque (pode ser "").
- selo: texto da etiqueta acima do titulo (padrao: "DICA DE IA").
Tudo que importa fica na faixa central, para nao ser cortado na grade do perfil.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
YEL = (255, 212, 0)
CY = (0, 204, 255)
WHITE = (245, 246, 250)
MUT = (150, 158, 185)

FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
if not os.path.exists(FB):
    FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM = FB.replace("Bold", "Medium") if os.path.exists(FB.replace("Bold", "Medium")) else FB


def F(size, medium=False):
    return ImageFont.truetype(FM if medium else FB, size)


def fundo():
    bg = Image.new("RGB", (W, H), (8, 9, 14))
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(16, 18, 26))
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(16, 18, 26))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W / 2 - 560, 380, W / 2 + 560, 1560], fill=90)
    bg = Image.composite(Image.new("RGB", (W, H), (20, 60, 130)), bg, glow.filter(ImageFilter.GaussianBlur(220)))
    return bg.convert("RGBA")


def logo_recortada(lado):
    lg = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
    # o fundo da logo e quase preto: vira transparente
    px = lg.load()
    for y in range(lg.height):
        for x in range(lg.width):
            r, g, b, a = px[x, y]
            if r < 45 and g < 50 and b < 62:
                px[x, y] = (r, g, b, 0)
    return lg.resize((lado, int(lado * lg.height / lg.width)), Image.LANCZOS)


def quebrar(palavras, fonte, largura, d):
    linhas, cur = [], []
    for w in palavras:
        teste = " ".join(cur + [w])
        if cur and d.textlength(teste, font=fonte) > largura:
            linhas.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        linhas.append(cur)
    return linhas


def gerar(titulo, destaque, saida, selo="DICA DE IA"):
    img = fundo()
    d = ImageDraw.Draw(img)

    # logo centralizada no alto da area segura, com brilho
    lado = 330
    lg = logo_recortada(lado)
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse([W / 2 - 230, 300, W / 2 + 230, 760], fill=120)
    img = Image.composite(Image.new("RGBA", (W, H), CY + (255,)), img, halo.filter(ImageFilter.GaussianBlur(90)))
    img.alpha_composite(lg, (int((W - lg.width) / 2), 360))
    d = ImageDraw.Draw(img)

    # selo
    fs = F(46)
    tw = d.textlength(selo, font=fs)
    x0, y0 = (W - tw) / 2 - 38, 760
    d.rounded_rectangle([x0, y0, x0 + tw + 76, y0 + 84], radius=42, fill=CY)
    d.text((x0 + 38, y0 + 12), selo, font=fs, fill=(8, 9, 14))

    # titulo com destaque em amarelo, auto ajuste de tamanho
    palavras = titulo.split()
    norm = lambda w: w.lower().strip(".,!?:")
    alvo_seq = [norm(w) for w in destaque.split()]
    marcadas = set()
    for i in range(len(palavras) - len(alvo_seq) + 1):
        if alvo_seq and [norm(w) for w in palavras[i:i + len(alvo_seq)]] == alvo_seq:
            marcadas = set(range(i, i + len(alvo_seq)))
            break
    for size in (118, 108, 98, 88, 80, 72):
        f = F(size)
        linhas = quebrar(palavras, f, W - 140, d)
        if len(linhas) <= 4:
            break
    lh = int(size * 1.18)
    y = 920 + max(0, (4 - len(linhas))) * lh // 3
    idx = 0
    for ln in linhas:
        largura = d.textlength(" ".join(ln), font=f)
        x = (W - largura) / 2
        for w in ln:
            cor = YEL if idx in marcadas else WHITE
            idx += 1
            d.text((x + 4, y + 5), w, font=f, fill=(0, 0, 0, 160))
            d.text((x, y), w, font=f, fill=cor)
            x += d.textlength(w + " ", font=f)
        y += lh

    # rodape da marca
    fr = F(44)
    marca = "@issoedica"
    d.text(((W - d.textlength(marca, font=fr)) / 2, 1640), marca, font=fr, fill=WHITE)
    fm = F(34, medium=True)
    sub = "IA prática para o seu negócio"
    d.text(((W - d.textlength(sub, font=fm)) / 2, 1705), sub, font=fm, fill=MUT)
    d.line([(W / 2 - 60, 1625), (W / 2 + 60, 1625)], fill=CY, width=5)

    img.convert("RGB").save(saida, "JPEG", quality=92)
    return saida


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    gerar(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "DICA DE IA")
    print("capa ok:", sys.argv[3])
