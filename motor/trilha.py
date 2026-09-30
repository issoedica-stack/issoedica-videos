"""Trilha eletronica gerada por codigo (sem direitos autorais): 108 bpm, Am-F-C-G,
kick + clap + hats + baixo + pad + arpejo, com impactos nas trocas de cena."""
import numpy as np, random
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100

def _lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def _hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def _bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
def _hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def _saw(f, n, det=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-det, 0, det) if det else (0,):
        ph = (t * f * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / (3 if det else 1)

def _env(n, a=0.005, d=0.1, s=0.0, r=0.05, hold=None):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    e = np.ones(n) * s
    e[:a_n] = np.linspace(0, 1, a_n) if a_n else 1
    end_d = min(n, a_n + d_n)
    e[a_n:end_d] = np.linspace(1, s, end_d - a_n) if end_d > a_n else s
    if r_n and n > r_n: e[-r_n:] *= np.linspace(1, 0, r_n)
    return e

def _add(buf, x, pos):
    i = int(pos * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]

def gerar(total, cortes, saida, seed=7):
    rnd = np.random.default_rng(seed)
    n = int((total + 0.5) * SR)
    kick, drums, bass, pad, arp, fx = (np.zeros(n) for _ in range(6))
    bpm = 108; beat = 60 / bpm; bar = 4 * beat
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    roots = [45, 41, 36, 43]
    intro = min(2.2, cortes[0] if cortes else 2.2)  # hook: sem bateria cheia
    # Kick
    kn = int(0.35 * SR); tk = np.arange(kn) / SR
    ksmp = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-tk * 28)) / SR) * np.exp(-tk * 9)
    ksmp += 0.3 * rnd.standard_normal(kn) * np.exp(-tk * 300)
    # Clap
    cn = int(0.25 * SR); tc = np.arange(cn) / SR
    clap = _bp(rnd.standard_normal(cn), 900, 5000) * np.exp(-tc * 18)
    # Hat
    hn = int(0.06 * SR); th = np.arange(hn) / SR
    hat = _hp(rnd.standard_normal(hn), 7000) * np.exp(-th * 70)
    t = 0.0; b = 0
    while t < total:
        ci = b % 4
        chord = prog[ci]
        # Pad (acorde do compasso)
        pn = int(bar * SR)
        p = sum(_saw(_hz(m), pn, 0.006) for m in chord) / 3
        p = _lp(p, 1400) * _env(pn, a=0.25, d=0.2, s=0.8, r=0.3)
        _add(pad, p, t)
        for s16 in range(16):
            ts = t + s16 * beat / 4
            if ts >= total: break
            full = ts >= intro
            if s16 % 4 == 0 and full: _add(kick, ksmp, ts)
            if s16 in (4, 12) and full: _add(drums, clap * 0.55, ts)
            if full: _add(drums, hat * (0.35 if s16 % 2 else 0.18), ts)
            # Baixo em colcheias
            if s16 % 2 == 0 and full:
                bn = int(beat / 2 * SR)
                bs = _lp(_saw(_hz(roots[ci]), bn), 420) * _env(bn, d=0.18, s=0.3, r=0.04)
                _add(bass, bs, ts)
            # Arpejo pluck em semicolcheias
            if ts >= 0.6:
                nota = chord[[0, 1, 2, 1][s16 % 4]] + 12 + (12 if s16 >= 8 else 0)
                an = int(0.18 * SR)
                a = _lp(_saw(_hz(nota), an, 0.003), 2600) * _env(an, d=0.14, s=0, r=0.02)
                _add(arp, a * 0.5, ts)
        t += bar; b += 1
    # Delay no arpejo
    dl = int(beat * 0.75 * SR)
    arp_d = arp.copy(); arp_d[dl:] += 0.35 * arp[:-dl]
    # Impactos + whoosh nas trocas de cena
    for c in cortes:
        wn = int(0.5 * SR); tw = np.linspace(0, 1, wn)
        w = _bp(rnd.standard_normal(wn), 400, 6000) * (tw ** 2) * 0.5
        _add(fx, w, max(0, c - 0.5))
        imn = int(0.8 * SR); ti = np.arange(imn) / SR
        _add(fx, np.sin(2 * np.pi * 42 * ti) * np.exp(-ti * 5) * 0.8, c)
    # Sidechain (duck pad/baixo no kick)
    sc = np.ones(n); step = beat
    k = 0.0
    while k < total:
        if k >= intro:
            i = int(k * SR); m = min(n, i + int(0.22 * SR))
            sc[i:m] = np.minimum(sc[i:m], 0.35 + 0.65 * np.linspace(0, 1, m - i))
        k += step
    mix = (kick * 0.9 + drums * 0.8 + bass * sc * 0.55 + pad * sc * 0.28 + arp_d * 0.30 + fx * 0.6)
    mix = _hp(mix, 30)
    fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
    mix[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
    st = np.stack([mix, mix], 1)
    wavfile.write(saida, SR, (st * 32767).astype(np.int16))
    return saida
