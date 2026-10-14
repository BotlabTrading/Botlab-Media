"""Genera la historia de Instagram de BoTlab a partir de data/AAAA-MM-DD.json.
Uso: python3 scripts/render.py 2026-10-14  -> historias/2026-10-14.png
"""
import json, sys, pathlib, datetime
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIAS = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

def pct(v, sign=True):
    s = f"{v:+.2f}%" if sign else f"{v:.2f}%"
    return s.replace(".", ",")

def main(date):
    d = json.loads((ROOT/"data"/f"{date}.json").read_text(encoding="utf-8"))
    dt = datetime.date.fromisoformat(date)
    weekly = d.get("weekly", False)
    hero_val = d["week"] if weekly else d["day"]
    vals = {
        "FECHA": f"{DIAS[dt.weekday()]} · {dt.day} de {MESES[dt.month-1]} de {dt.year}",
        "HEROLBL": "RESULTADO DE LA SEMANA" if weekly else "RESULTADO DEL DÍA",
        "HOY": pct(hero_val),
        "SEM": pct(d["day"]) if weekly else pct(d["week"]),
        "MES": pct(d["month"]), "ANO": pct(d["year"]),
        "DD": pct(d["maxdd"], False), "WR": f"{d['winrate']:.1f}%".replace(".", ","),
    }
    h = (ROOT/"scripts"/"story.html").read_text(encoding="utf-8")
    if weekly:
        h = h.replace("<span>Semana</span>", "<span>Viernes</span>")
    h = h.replace("__LOGO__", (ROOT/"scripts"/"logo.png").as_uri())
    for k, v in vals.items():
        h = h.replace(f"__{k}__", v)
    for k, key in [("CH","HOY"),("CS","SEM"),("CM","MES"),("CA","ANO")]:
        h = h.replace(f"__{k}__", "neg" if vals[key].startswith("-") else "pos")
    tmp = ROOT/"scripts"/"_out.html"; tmp.write_text(h, encoding="utf-8")
    out = ROOT/"historias"/f"{date}.png"; out.parent.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width":1080,"height":1920})
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(400); pg.screenshot(path=str(out)); b.close()
    tmp.unlink()
    print(out)

if __name__ == "__main__":
    main(sys.argv[1])
