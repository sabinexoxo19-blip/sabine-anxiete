"""Lots Pinterest du livre 2 : 1 image à 11 h 15 + 1 vidéo à 21 h 15 (heure de Paris), par lots de 14 jours.

Pourquoi des lots de 14 jours : un compte Pinterest refuse tout au-delà de 100 épingles programmées,
et le livre 1 partage ce plafond. Importer chaque lot 2 ou 3 jours avant sa première date.

Usage :  python3 pines_lots.py --base https://utilisateur.github.io/depot
         [--debut 2026-11-07T21:15] [--image 52] [--video 1]
         --debut : premier créneau (heure de Paris) ; --image / --video : premiers numéros à publier
"""
import argparse
import csv
import glob
import json
import os
import sys
from datetime import datetime, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from frases import FRASES                                                   # noqa: E402
from pines import LIEN, TABLEAUX, date_utc, description as desc_image, tableau, titre   # noqa: E402
from pines_video import description as desc_video, miniature                # noqa: E402

RAIZ = os.path.dirname(AQUI)
CRENEAUX = [((11, 15), "image"), ((21, 15), "video")]   # livre 1 : 12 h 15 et 20 h 45
JOURS_PAR_LOT = 14


def ligne_image(i, base):
    f = FRASES[i]
    cle = tableau(i, f)
    return {"Title": titre(f, cle), "Media URL": f"{base}/pines/{i + 1:04d}.jpg",
            "Pinterest board": TABLEAUX[cle][0], "Thumbnail": "", "Description": desc_image(f),
            "Link": f"{LIEN}/ref=pin2_{i + 1:04d}", "Keywords": TABLEAUX[cle][2]}


def ligne_video(i, c, base):
    f = FRASES[i]
    cle = tableau(i, f)
    return {"Title": titre(f, cle), "Media URL": f"{base}/posts/{c['archivo']}",
            "Pinterest board": TABLEAUX[cle][0], "Thumbnail": miniature(c.get("portada_ms")),
            "Description": desc_video(f, c.get("fin_livre")),
            "Link": f"{LIEN}/ref=pin2v_{i + 1:04d}", "Keywords": TABLEAUX[cle][2]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--debut", default="2026-11-07T21:15")   # la dernière épingle livre 2 déjà programmée : 07/11 10 h 15
    ap.add_argument("--image", type=int, default=52)          # pin2_0052 à 0059 refusées par Pinterest (plafond de 100)
    ap.add_argument("--video", type=int, default=1)
    a = ap.parse_args()
    base = a.base.rstrip("/")

    with open(os.path.join(RAIZ, "cola.json"), encoding="utf-8") as fh:
        cola = json.load(fh)
    images = list(range(a.image - 1, len(FRASES)))
    videos = list(range(a.video - 1, len(cola)))
    for i in images:
        if not os.path.exists(os.path.join(RAIZ, "pines", f"{i + 1:04d}.jpg")):
            sys.exit(f"Image absente : pines/{i + 1:04d}.jpg")
    for i in videos:
        if not os.path.exists(os.path.join(RAIZ, "posts", cola[i]["archivo"])):
            sys.exit(f"Vidéo absente : posts/{cola[i]['archivo']}")

    debut = datetime.fromisoformat(a.debut)
    jour, lignes = debut.date(), []
    while images or videos:
        for (h, m), genre in CRENEAUX:
            if datetime(jour.year, jour.month, jour.day, h, m) < debut:
                continue
            if genre == "image" and images:          # plus d'images : le créneau du matin prend une vidéo
                l = ligne_image(images.pop(0), base)
            elif videos:
                i = videos.pop(0)
                l = ligne_video(i, cola[i], base)
            elif images:
                l = ligne_image(images.pop(0), base)
            else:
                break
            l["Publish date"] = date_utc(jour, h, m)
            l["_jour"] = jour
            lignes.append(l)
        jour += timedelta(days=1)

    for ancien in glob.glob(os.path.join(RAIZ, "pinterest2_lot*.csv")):
        os.remove(ancien)
    champs = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
    n = 0
    while lignes:
        n += 1
        fin = lignes[0]["_jour"] + timedelta(days=JOURS_PAR_LOT)
        lot = [l for l in lignes if l["_jour"] < fin]
        lignes = lignes[len(lot):]
        nom = f"pinterest2_lot{n:02d}.csv"
        with open(os.path.join(RAIZ, nom), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=champs, extrasaction="ignore")
            w.writeheader()
            w.writerows(lot)
        importer = lot[0]["_jour"] - timedelta(days=3)
        print(f"{nom} : {len(lot)} épingles, du {lot[0]['_jour']:%d/%m} au {lot[-1]['_jour']:%d/%m} "
              f"— à importer le {importer:%d/%m/%Y} (ou jusqu’à 2 jours avant)")


if __name__ == "__main__":
    main()
