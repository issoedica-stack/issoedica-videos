"""Escolhe o tema visual do dia: o primeiro do rodízio que não apareceu nos últimos 3 vídeos.
Uso: python3 motor/tema_pick.py   (imprime o nome do tema)"""
import glob, json, re
TEMAS = ["neon", "oceano", "brasa", "lima", "magenta", "editorial"]
usados = []
for f in sorted(glob.glob("tutorial/*.json"), reverse=True):
    if f.endswith(".roteiro.json") or f.endswith("indice.json"): continue
    try: t = json.load(open(f)).get("tema")
    except Exception: continue
    if t: usados.append(t)
recentes = usados[:3]
ult = usados[0] if usados else None
i0 = (TEMAS.index(ult) + 1) if ult in TEMAS else 0
for k in range(len(TEMAS)):
    t = TEMAS[(i0 + k) % len(TEMAS)]
    if t not in recentes:
        print(t); break
