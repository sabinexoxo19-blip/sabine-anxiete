"""Reel test avec la vraie voix (Azure) : fabrique essais/test.mp4 et essais/test.jpg.

Usage : python3 test_reel.py [numéro dans frases.py, 1 par défaut] [fin livre : 1 ou 0, 1 par défaut]
Ne touche ni à cola.json ni aux posts : c'est seulement un essai à regarder.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.dirname(AQUI))
from frases import FRASES              # noqa: E402
from generar_b import generar          # noqa: E402
import voz                             # noqa: E402
import poner_musica                    # noqa: E402

RAIZ = os.path.dirname(AQUI)
SORTIE = os.path.join(RAIZ, "essais")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else 1
    fin = (sys.argv[2] if len(sys.argv) > 2 else "1") == "1"
    f = FRASES[n - 1]
    os.makedirs(SORTIE, exist_ok=True)
    voces = voz.lire_reel(f["hook"], f["texto"])          # même voix et même débit que la production
    mp4, jpg = os.path.join(SORTIE, "test.mp4"), os.path.join(SORTIE, "test.jpg")
    dur, _ = generar(f["hook"], f["texto"], mp4, jpg, seed=1000 + n, numero=f["n"], voces=voces,
                     fin_livre=os.path.join(AQUI, "libro_1.jpg") if fin else None)
    pistas = poner_musica.musiques()
    if pistas:
        poner_musica.mezclar(mp4, pistas[0], dur, avec_voix=True)
    print(f"essais/test.mp4 prêt ({dur:.1f} s)", flush=True)


if __name__ == "__main__":
    main()
