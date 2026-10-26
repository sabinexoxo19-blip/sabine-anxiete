# Robot Instagram et Pinterest — livre 2 de Sabine Mercier

Livre : *101 Vérités que ton anxiété essaie de te dire* — https://www.amazon.fr/dp/B0GR8JW5V7

Depuis fin octobre 2026, le robot publie **101 Reels « livre ouvert »** (une vérité par Reel, vraies pages du livre, 13 s, musique au piano), lus dans la file `cola_livre.json` et rangés dans `posts/r001.mp4` à `posts/r101.mp4`, **3 fois par jour** (la vérité 97 est retirée : 100 Reels publiés). Les mêmes Reels partent en **YouTube Shorts** sur la chaîne Sabine Mercier (celle du livre 1), 2 par jour, depuis `cola_youtube.json`. L'ancienne file `cola.json` (Reels lus par une voix) n'est plus publiée : elle sert d'historique. Le robot prépare aussi les **épingles Pinterest** à importer en bloc. Ton ordinateur n'a pas besoin d'être allumé.

Le robot du livre 1 (dépôt `sabine-reels`) est totalement séparé : rien ici ne le touche.

---

## Comment ça marche

1. **GitHub** garde le robot, fabrique les vidéos et les met en ligne (GitHub Pages).
2. **Azure** prête la voix « Vivienne » (ressource `sabine-voix`, la même que le livre 1). Le palier gratuit suffit : 120 Reels font environ 40 000 caractères, le gratuit en donne 500 000 par mois, pour les deux livres ensemble.
3. **cron-job.org** réveille le robot toutes les 30 minutes (à :20 et :50). Le robot ne publie qu'aux créneaux.

Publication : **7 h 47, 13 h 17 et 18 h 47, heure de Paris** (décalés de ceux du livre 1 : 8 h 12, 12 h 42, 20 h 12 ; changement d'heure géré tout seul). Un créneau manqué depuis plus de 2 h est abandonné ; jamais deux Reels à moins de 2 h d'écart, y compris avec la dernière publication de l'ancienne file.

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
| **Publier sur Instagram** | réveils automatiques | publie le Reel suivant de `cola_livre.json`. À la main : **1** = essai, **0** = publier. |
| **Renouveler la clé Instagram** | chaque lundi | prolonge `IG_TOKEN` (seulement si la clé a plus de 24 h). |
| **Ajouter la musique** | quand des musiques sont ajoutées | refait le son des Reels pas encore publiés. |
| **Fabriquer les épingles Pinterest** | à la main | images `pines/` (déjà faites) |
| **Lots Pinterest (images + vidéos)** | à la main, une fois | fichiers `pinterest2_lot01.csv`, `pinterest2_lot02.csv`… (14 jours chacun) |
| **Reel test avec la voix** / **Essai format B** | à la main | Reels d'essai dans `essais/`. |

---

## YouTube Shorts (même chaîne que le livre 1)

- **10 h 47 et 16 h 47**, heure de Paris (le livre 1 publie à 13 h 12 et 19 h 42 sur la même chaîne).
- Secrets : `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` (même projet Google que le livre 1). Sans eux, l'étape YouTube ne fait rien.
- Si YouTube garde un Short en privé, le robot s'arrête de lui-même (`prive` dans `cola_youtube.json`).

## Pinterest (même compte que le livre 1)

- Import en bloc : https://fr.pinterest.com/settings/bulk-create-pins/
- **Plafond : 100 épingles programmées par compte, livre 1 et livre 2 ensemble.** Au-delà, Pinterest refuse les lignes (e-mail « Plus de 100 Épingles programmées »).
- Jusqu'au 7 novembre 2026 : images à 10 h 15 et 22 h 15 (`pinterest2_prueba.csv`, `pinterest2_mois1.csv`, déjà importés ; `pin2_0052` à `0059` refusées par le plafond, reprises dans le lot 01).
- À partir du 7 novembre 2026 au soir : **1 image à 11 h 15 + 1 vidéo à 21 h 15** (heure de Paris ; le livre 1 publie à 12 h 15 et 20 h 45).
- Depuis le 26 octobre 2026, les épingles vidéo sont les Reels « livre ouvert » (`posts/r001.mp4`…, miniature dans `miniatures/`) : `pinterest2_lot00.csv` (1 vidéo par jour à 21 h 15, du 27 octobre au 6 novembre), puis les vidéos des lots 01 à 06 ; les derniers créneaux gardent d'anciens Reels lus par la voix.
- Fichiers `pinterest2_lot01.csv`, `lot02`… : 14 jours chacun, **à importer 2 ou 3 jours avant leur première date**, jamais plus tôt (plafond).
- Tableaux propres au livre 2 : « Anxiété : comprendre et apaiser », « Anxiété et corps : respiration, sommeil, détente », « Pensées anxieuses et ruminations », « Citations anxiété et bienveillance ».
- Un lien différent par épingle : `…/ref=pin2_0001` (images), `…/ref=pin2v_0001` (vidéos).
- Les vidéos sont les Reels de `posts/` ; image de couverture = celle d'Instagram ; description avec « Voix de synthèse ».

---

## Les mentions obligatoires

- Reels « livre ouvert » : la légende porte « Images créées par IA, pages réelles du livre. » et, pour les vérités sur l'angoisse, les crises ou les symptômes, « Ce livre ne remplace pas l'accompagnement d'un professionnel de santé. »

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
| E-mail Pinterest « Plus de 100 Épingles programmées » | lot importé trop tôt : réimporter le même fichier plus tard (pas de doublon) |
| cron-job.org affiche 401 ou 403 | le jeton « reveil livre 2 » a expiré : en créer un nouveau |

---

Polices libres (licence SIL OFL, `fabrica/licences`) : DM Serif Display, EB Garamond, Caveat, Jost. Musiques : pixabay.com/music (licence Pixabay).
