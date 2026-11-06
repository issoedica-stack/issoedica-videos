"""Confere se uma abertura repete vídeos anteriores.
Uso: python3 motor/gancho_check.py "<frase de abertura>" [formato] [--ignore=<ID do vídeo de hoje>]
Lê tutorial/*.json (narracao[0] e campo gancho) e os roteiros (1ª linha do kinetic)."""
import glob, json, re, sys, unicodedata
def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", s)
BAN = ["pouca gente sabe", "voce sabia", "sabia que", "olha o que", "truque"]
args = [a for a in sys.argv[1:] if not a.startswith("--ignore=")]
IGN = [a.split("=",1)[1] for a in sys.argv[1:] if a.startswith("--ignore=")]
frase = args[0]; fmt = args[1] if len(args) > 1 else None
w = norm(frase); erros = []
if any(" ".join(w).startswith(b) or b in " ".join(w[:4]) for b in BAN): erros.append("abertura proibida")
hist = []
for f in sorted(glob.glob("tutorial/*.json"), reverse=True):
    if any(f.split("/")[-1].startswith(i) for i in IGN): continue
    try: d = json.load(open(f))
    except Exception: continue
    if not isinstance(d, dict): continue
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
