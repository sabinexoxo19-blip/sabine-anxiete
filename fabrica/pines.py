"""Fabrique les épingles Pinterest (pines/NNNN.jpg) et les fichiers CSV d'import en bloc
(Pinterest → Créer → Créer des épingles en bloc).

Usage :  python3 pines.py --base https://utilisateur.github.io/depot [--inicio 2026-10-10] [--prueba]
         --prueba : 3 épingles seulement, dans pinterest2_prueba.csv
"""
import argparse
import csv
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta, timezone
from multiprocessing import Pool
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from frases import FRASES          # noqa: E402

RAIZ = os.path.dirname(AQUI)
DOSSIER = os.path.join(RAIZ, "pines")
LIEN = "https://www.amazon.fr/dp/B0GR8JW5V7"
LIVRE = "« 101 vérités que ton anxiété essaie de te dire » de Sabine Mercier"
PARIS = ZoneInfo("Europe/Paris")
HEURES = [(10, 15), (22, 15)]       # heure de Paris (livre 1 : 12 h 15 et 20 h 45) ; heure d'hiver calculée
PAR_CSV = 56                        # 28 jours par fichier (Pinterest programme 30 jours à l’avance au maximum)

# (tableau, préfixe du titre, mots-clés) — tableaux propres au livre 2 (ceux du livre 1 ne sont pas touchés)
TABLEAUX = {
    "anxiete": ("Anxiété : comprendre et apaiser", "Anxiété",
                "anxiété, angoisse, apaiser son anxiété, confiance en soi"),
    "corps": ("Anxiété et corps : respiration, sommeil, détente", "Anxiété",
              "respiration anxiété, insomnie anxiété, stress et corps, se détendre"),
    "pensees": ("Pensées anxieuses et ruminations", "Pensées anxieuses",
                "pensées anxieuses, rumination, arrêter de trop penser, peur de l'avenir"),
    "citations": ("Citations anxiété et bienveillance", "Citation",
                  "citation anxiété, citations bienveillance, phrase apaisante, développement personnel"),
}
MOTS_CORPS = re.compile(r"cœur|souffle|respir|inspire|expire|dormi|sommeil|nuit|ventre|corps|mâchoire|marche|"
                        r"en place|énergie|calme te|matin", re.I)
MOTS_PENSEES = re.compile(r"pensée|penser|pensent|cerveau|rumin|« et si|imagin|pire|vérifi|certitude|futur|"
                          r"deviner|esprit|raté|parfait|devrais|chance|sais pas|attention", re.I)


def sans_emoji(t):
    t = "".join(c for c in t if unicodedata.category(c) not in ("So", "Sk", "Cs", "Mn") or c in "’«»")
    t = t.replace("️", "")
    return re.sub(r"\s+", " ", t).strip()


def propre(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("\n", " ")).strip()


def tableau(i, f):
    if MOTS_CORPS.search(f["hook"]):
        return "corps"
    if MOTS_PENSEES.search(f["hook"]):
        return "pensees"
    return ["anxiete", "citations"][i % 2]


def titre(f, cle):
    h = propre(f["hook"]).rstrip(".")
    k = next((j for j, c in enumerate(h) if c.isalpha()), 0)
    if not h[k:].startswith(("J’", "J'", "« ")) and not h[k:k + 2].isupper():
        h = h[:k] + h[k].lower() + h[k + 1:]
    prefixe = TABLEAUX[cle][1]
    if prefixe.split()[0].lower()[:6] in h.lower():      # « Anxiété : ton anxiété… » : préfixe inutile
        t = (h[:k] + h[k].upper() + h[k + 1:]).replace("'", "’")
    else:
        t = f"{prefixe} : {h}".replace("'", "’")
    return t if len(t) <= 100 else t[:97].rsplit(" ", 1)[0] + "…"


def description(f):
    d = (f"{propre(f['hook'])} {sans_emoji(f['leyenda'])} "
         f"Une vérité du livre {LIVRE}, pour comprendre et apaiser ton anxiété, sans te juger. "
         f"Enregistre-la pour les jours où tu en as besoin.")
    return d.replace("'", "’")[:500]


def tache(i):
    from pin import generar_pin
    f = FRASES[i]
    generar_pin(f["hook"], sans_emoji(f["leyenda"]), os.path.join(DOSSIER, f"{i + 1:04d}.jpg"),
                numero=f["n"], seed=2000 + i)
    return i


def date_utc(jour, h, m):
    local = datetime(jour.year, jour.month, jour.day, h, m, tzinfo=PARIS)
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--inicio", default="")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    debut = date.fromisoformat(a.inicio) if a.inicio else date.today() + timedelta(days=1)

    os.makedirs(DOSSIER, exist_ok=True)
    indices = list(range(3)) if a.prueba else list(range(len(FRASES)))
    a_faire = [i for i in indices if a.prueba or not os.path.exists(os.path.join(DOSSIER, f"{i + 1:04d}.jpg"))]
    with Pool(os.cpu_count() or 2) as p:
        for i in p.imap_unordered(tache, a_faire):
            print(f"épingle {i + 1:04d}", flush=True)

    lignes = []
    for n, i in enumerate(indices):
        f = FRASES[i]
        cle = tableau(i, f)
        jour = debut + timedelta(days=n // len(HEURES))
        h, m = HEURES[n % len(HEURES)]
        lignes.append({
            "Title": titre(f, cle),
            "Media URL": f"{a.base.rstrip('/')}/pines/{i + 1:04d}.jpg",
            "Pinterest board": TABLEAUX[cle][0],
            "Thumbnail": "",
            "Description": description(f),
            "Link": f"{LIEN}/ref=pin2_{i + 1:04d}",      # un lien différent par épingle (pin2_ = livre 2)
            "Publish date": date_utc(jour, h, m),
            "Keywords": TABLEAUX[cle][2],
        })

    essai = os.path.join(RAIZ, "pinterest2_prueba.csv")
    if not a.prueba and os.path.exists(essai):          # épingles déjà importées avec l’essai : pas de doublon
        with open(essai, encoding="utf-8") as fh:
            deja = {r["Link"] for r in csv.DictReader(fh)}
        lignes = [l for l in lignes if l["Link"] not in deja]
        print(f"{len(deja)} épingles de l’essai déjà importées : retirées des fichiers du mois.")

    groupes = [lignes] if a.prueba else [lignes[k:k + PAR_CSV] for k in range(0, len(lignes), PAR_CSV)]
    for g_i, groupe in enumerate(groupes, start=1):
        nom = "pinterest2_prueba.csv" if a.prueba else f"pinterest2_mois{g_i}.csv"
        with open(os.path.join(RAIZ, nom), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(groupe[0].keys()))
            w.writeheader()
            w.writerows(groupe)
        print(nom, len(groupe), "épingles, du", groupe[0]["Publish date"], "au", groupe[-1]["Publish date"], "(UTC)")


if __name__ == "__main__":
    main()
