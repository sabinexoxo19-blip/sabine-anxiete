# Robot Instagram et Pinterest — livre 2 de Sabine Mercier

Livre : *101 Vérités que ton anxiété essaie de te dire* — https://www.amazon.fr/dp/B0GR8JW5V7

Ce dépôt fabrique **120 Reels** lus par une voix (30 jours ; 1 sur 4 se termine sur la photo du livre, avec le lien dans la légende), puis **les publie tout seul, 4 fois par jour**. Il fabrique aussi les **épingles Pinterest** (2 par jour) à importer en bloc. Ton ordinateur n'a pas besoin d'être allumé.

Le robot du livre 1 (dépôt `sabine-reels`) est totalement séparé : rien ici ne le touche.

---

## Comment ça marche

1. **GitHub** garde le robot, fabrique les vidéos et les met en ligne (GitHub Pages).
2. **Azure** prête la voix « Vivienne » (ressource `sabine-voix`, la même que le livre 1). Le palier gratuit suffit : 120 Reels font environ 40 000 caractères, le gratuit en donne 500 000 par mois, pour les deux livres ensemble.
3. **cron-job.org** réveille le robot toutes les 30 minutes (à :20 et :50). Le robot ne publie qu'aux créneaux.

Publication : **7 h 47, 12 h 47, 18 h 47 et 22 h 17, heure de Paris** (décalés de ceux du livre 1 ; changement d'heure géré tout seul). Un créneau manqué depuis plus de 2 h est abandonné ; jamais deux Reels à moins de 2 h d'écart.

---

## Les 4 clés secrètes (dans GitHub, jamais ailleurs)

| Nom | Ce que c'est |
|---|---|
| `AZURE_SPEECH_KEY` | clé 1 de la ressource Azure `sabine-voix` |
| `AZURE_SPEECH_REGION` | `swedencentral` |
| `IG_TOKEN` | clé Instagram du compte du livre 2 (60 jours, renouvelée chaque lundi) |
| `GH_PAT` | jeton GitHub fine-grained limité à ce dépôt, droit « Secrets : Read and write » |

Dans cron-job.org : un jeton fine-grained **« reveil livre 2 »**, limité à ce dépôt, droit « Actions : Read and write ».

---

## Les automatismes (onglet Actions)

| Nom | Quand | Rôle |
|---|---|---|
| **Fabriquer les Reels** | à la main | vidéos (`posts/`) et file `cola.json`. S'il s'arrête, on le relance : il reprend où il en était. |
| **Publier sur Instagram** | réveils automatiques | publie le Reel suivant. À la main : **1** = essai, **0** = publier. |
| **Renouveler la clé Instagram** | chaque lundi | prolonge `IG_TOKEN` (seulement si la clé a plus de 24 h). |
| **Ajouter la musique** | quand des musiques sont ajoutées | refait le son des Reels pas encore publiés. |
| **Fabriquer les épingles Pinterest** | à la main | images `pines/` et fichiers `pinterest2_mois1.csv`, `pinterest2_mois2.csv`… |
| **Reel test avec la voix** / **Essai format B** | à la main | Reels d'essai dans `essais/`. |

---

## Pinterest (même compte que le livre 1)

- Import en bloc : https://fr.pinterest.com/settings/bulk-create-pins/
- 2 épingles par jour, **10 h 15 et 22 h 15** (heure de Paris ; le livre 1 publie à 12 h 15 et 20 h 45).
- Tableaux propres au livre 2 : « Anxiété : comprendre et apaiser », « Anxiété et corps : respiration, sommeil, détente », « Pensées anxieuses et ruminations », « Citations anxiété et bienveillance ».
- Un lien différent par épingle : `…/dp/B0GR8JW5V7/ref=pin2_0001`, `pin2_0002`…
- Fichiers `pinterest2_*.csv` (le « 2 » évite toute confusion avec ceux du livre 1). Pinterest programme 30 jours à l'avance au maximum : importer chaque fichier moins de 30 jours avant sa dernière date.
- Faire d'abord l'essai (3 épingles), vérifier dans « Épingles programmées » qu'elles sont bien 3.

---

## Les mentions obligatoires

- Chaque Reel lu par Vivienne porte **(voix de synthèse)**.
- Les Reels qui finissent sur la photo du livre portent aussi **(visuel créé par IA)** : la photo est une image IA.

---

## En cas de problème

| Message | Que faire |
|---|---|
| « Il manque le secret AZURE_SPEECH_KEY » | ajouter le secret, relancer **Fabriquer les Reels** |
| « Azure refuse la clé (erreur 401) » | recopier la clé 1 et la région depuis le portail Azure |
| « La vidéo n'est pas accessible » | GitHub Pages pas activé, ou attendre 5 minutes |
| « ERROR API … 190 » / « OAuthException » | la clé Instagram a expiré : en refaire une et remplacer `IG_TOKEN` |
| « La file est vide » | il faut un nouveau lot de Reels |
| cron-job.org affiche 401 ou 403 | le jeton « reveil livre 2 » a expiré : en créer un nouveau |

---

Polices libres (licence SIL OFL, `fabrica/licences`) : DM Serif Display, EB Garamond, Caveat, Jost. Musiques : pixabay.com/music (licence Pixabay).
