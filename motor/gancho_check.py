"""Confere se uma abertura repete vídeos anteriores.
Uso: python3 motor/gancho_check.py "<frase de abertura>" [formato]
Lê tutorial/*.json (narracao[0] e campo gancho) e os roteiros (1ª linha do kinetic)."""
import glob, json, re, sys, unicodedata
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", s)
BAN = ["pouca gente sabe", "voce sabia", "sabia que", "olha o que", "truque"]
frase = sys.argv[1]; fmt = sys.argv[2] if len(sys.argv) > 2 else None
w = norm(frase); erros = []
if any(" ".join(w).startswith(b) or b in " ".join(w[:4]) for b in BAN): erros.append("abertura proibida")
hist = []
for f in sorted(glob.glob("tutorial/*.json"), reverse=True):
    try: d = json.load(open(f))
    except Exception: continue
    if f.endswith(".roteiro.json"):
        for s in d.get("scenes", []):
            if s.get("type") == "kinetic": hist.append((f, " ".join(l[0] for l in s["lines"]), None)); break
    else:
        n = d.get("narracao"); t = d.get("gancho") or (n[0]["texto"] if isinstance(n, list) and n else "")
        if t: hist.append((f, t, d.get("gancho_formato")))
for f, t, _ in hist:
    if norm(t)[:3] == w[:3]: erros.append(f"mesmas 3 primeiras palavras de {f}: {t}")
if fmt:
    recentes = [str(x[2]) for x in hist if x[2] is not None][:10]
    if str(fmt) in recentes: erros.append(f"formato {fmt} usado nos últimos 10: {recentes}")
print("REPETIDO:\n- " + "\n- ".join(erros) if erros else "OK: abertura inédita")
sys.exit(1 if erros else 0)
