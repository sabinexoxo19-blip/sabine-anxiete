"""Banque de Reels — livre 2 de Sabine Mercier.

Source : « 101 vérités que ton anxiété essaie de te dire », Sabine Mercier.
Chaque entrée : n (numéro de la vérité, None = « 101 VÉRITÉS »), hook (3 ou 4 lignes, \n = saut),
texto (paragraphes lus par la voix et affichés un par un), leyenda (légende Instagram).
*mot* = écrit en corail manuscrit (un dans le hook, un dans le dernier paragraphe).

Pour l'instant : seulement le Reel test (vérité 1). La banque complète (120 Reels) viendra à l'étape C.
"""

FRASES = [
    # 1 — Reel test
    dict(n=1, hook="Ton anxiété n'est pas\nune faiblesse.\nC'est une alarme\ntrop *sensible*.",
         texto=["Ton cerveau est si doué pour repérer les menaces qu'il en voit même là où il n'y en a pas.",
                "C'est comme un détecteur de fumée qui se déclenche dès que tu fais griller du pain.",
                "Le problème n'est pas le détecteur. C'est son réglage.",
                "Tu n'es pas quelqu'un de défaillant. Tu es quelqu'un de *suréquipé.*"],
         leyenda="Tu n'as rien de défaillant. Ton alarme est juste réglée trop fort. 🔔"),
]
