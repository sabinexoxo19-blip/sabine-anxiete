"""Fichiers CSV d'import en bloc pour les épingles VIDÉO (les Reels déjà fabriqués dans posts/).
Rien à fabriquer : Pinterest va chercher chaque vidéo sur GitHub Pages.

Usage :  python3 pines_video.py --base https://utilisateur.github.io/depot [--inicio 2026-10-15] [--prueba]
         --prueba : 3 épingles vidéo seulement, dans pinterest2_video_prueba.csv
"""
import argparse
import csv
import json
import os
import sys
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from frases import FRASES                                            # noqa: E402
from pines import LIEN, LIVRE, TABLEAUX, date_utc, propre, sans_emoji, tableau, titre   # noqa: E402

RAIZ = os.path.dirname(AQUI)
HEURE = (16, 15)        # heure de Paris ; images livre 2 : 10 h 15 et 22 h 15 ; livre 1 : 12 h 15 et 20 h 45
PAR_CSV = 28            # 28 jours par fichier (Pinterest programme 30 jours à l'avance au maximum)


def miniature(ms):
    s = max(1, int(ms or 1000) // 1000)          # image de couverture = celle choisie pour Instagram
    return f"{s // 60:02d}:{s % 60:02d}"


def description(f, fin_livre):
    mention = "Voix de synthèse, visuel du livre créé par IA." if fin_livre else "Voix de synthèse."
    d = (f"{propre(f['hook'])} {sans_emoji(f['leyenda'])} "
         f"Une vérité du livre {LIVRE}, pour comprendre et apaiser ton anxiété, sans te juger. {mention}")
    return d.replace("'", "’")[:500]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--inicio", default="")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    debut = date.fromisoformat(a.inicio) if a.inicio else date.today() + timedelta(days=1)

    with open(os.path.join(RAIZ, "cola.json"), encoding="utf-8") as fh:
        cola = json.load(fh)
    par_verite = {i: c for i, c in enumerate(cola)}
    indices = list(range(3)) if a.prueba else list(range(len(cola)))

    lignes = []
    for i in indices:
        c, f = par_verite[i], FRASES[i]
        if not os.path.exists(os.path.join(RAIZ, "posts", c["archivo"])):
            sys.exit(f"Vidéo absente : posts/{c['archivo']}")
        cle = tableau(i, f)
        lignes.append({
            "Title": titre(f, cle),
            "Media URL": f"{a.base.rstrip('/')}/posts/{c['archivo']}",
            "Pinterest board": TABLEAUX[cle][0],
            "Thumbnail": miniature(c.get("portada_ms")),
            "Description": description(f, c.get("fin_livre")),
            "Link": f"{LIEN}/ref=pin2v_{i + 1:04d}",     # pin2v_ = livre 2, épingle vidéo
            "Publish date": "",
            "Keywords": TABLEAUX[cle][2],
        })

    essai = os.path.join(RAIZ, "pinterest2_video_prueba.csv")
    if not a.prueba and os.path.exists(essai):           # vidéos déjà importées avec l'essai : pas de doublon
        with open(essai, encoding="utf-8") as fh:
            deja = {r["Link"] for r in csv.DictReader(fh)}
        lignes = [l for l in lignes if l["Link"] not in deja]
        print(f"{len(deja)} épingles vidéo de l'essai déjà importées : retirées des fichiers du mois.")

    for n, l in enumerate(lignes):                        # une par jour, à 16 h 15
        l["Publish date"] = date_utc(debut + timedelta(days=n), *HEURE)

    groupes = [lignes] if a.prueba else [lignes[k:k + PAR_CSV] for k in range(0, len(lignes), PAR_CSV)]
    for g_i, groupe in enumerate(groupes, start=1):
        nom = "pinterest2_video_prueba.csv" if a.prueba else f"pinterest2_video_mois{g_i}.csv"
        with open(os.path.join(RAIZ, nom), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(groupe[0].keys()))
            w.writeheader()
            w.writerows(groupe)
        print(nom, len(groupe), "épingles vidéo, du", groupe[0]["Publish date"], "au",
              groupe[-1]["Publish date"], "(UTC)")


if __name__ == "__main__":
    main()
