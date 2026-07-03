# 📡 Radio Streaming Analytics — Projet MongoDB 

Application NoSQL de radio en ligne : une plateforme qui centralise des stations du monde entier, leurs flux audio, les morceaux diffusés et les artistes associés. Elle permet d’analyser les tendances, consulter l’historique, recommander des stations et exposer ces données via API et interface web dynamique.


> Ce projet a pour objectif de modéliser et analyser des données issues du réseau iHeartRadio afin de comprendre la dynamique des stations, des morceaux diffusés, des artistes et des marchés radio.
> Il s’inscrit dans une démarche de structuration de données non relationnelles, d’analyse métier et de mise en place d’un modèle NoSQL cohérent et exploitable.

---

## 🎯 Choix du sujet

Le domaine de la radio est particulièrement intéressant pour un projet NoSQL car il implique :

    - des **données hétérogènes** (stations, artistes, morceaux, flux audio, marchés géographiques)  
    - des **relations multiples** (une station diffuse plusieurs morceaux, un morceau peut avoir plusieurs artistes, un artiste peut être diffusé sur plusieurs stations)  
    - des **événements temporels** (plays, timestamps, audience)  
    - des **structures flexibles** (genres, réseaux sociaux, URLs de streaming)

MongoDB est donc un excellent choix pour représenter ce type de données, car il permet d’imbriquer des documents, de gérer des listes, et de modéliser des entités complexes sans contrainte de schéma strict.

## 📁 Le dataset 

> Ce dataset est adapté à un projet NoSQL car il contient des entités métier (stations, morceaux, artistes, diffusions) et un volume potentiellement important d’événements de diffusion. La structure documentaire de MongoDB permet de modéliser ces données de manière flexible, d’ajouter des métadonnées, et de répondre à des besoins d’analyse et de recommandation propres à une application de radio en ligne.

Le dataset source contient **2 entités brutes seulement** :

| Entité source | Volume échantillon utilisé |
|---|---|
| `stations` | 3 772 stations |
| `station-plays` | 10 000 lignes (1 jour — 20/04/2026) |

Il n'existe pas d'entité `tracks`/`artists` séparée côté source : ces infos sont imbriquées à plat dans chaque ligne de `station-plays` (titre, artiste, album, durée, `trackId`, `artistId`). C'est notre travail de modélisation qui les a extraites en collections normalisées à part, pour éviter la duplication massive de ces informations sur un très grand nombre d'événements de diffusion.

Ses catactéristiques :

- Richesse des entités : le dataset contient au moins des stations, des morceaux (tracks), des artistes, et des événements de diffusion (plays).
- Données semi-structurées : certaines colonnes peuvent être enrichies (tags, genres multiples, métadonnées), ce qui se prête bien à des documents JSON.
- Volume et historique : les plays (diffusions) peuvent être très nombreux → NoSQL (MongoDB) est adapté pour stocker des logs d’événements.
- Flexibilité du schéma : il est possible d'ajouter des champs (popularité, tendances, recommandations) sans casser le schéma → typique d’un projet NoSQL.
- Cas d’usage réel : via ce dataset notre application de radio en ligne peut :
    - lister des stations
    - voir ce qui est diffusé
    - analyser les tendances
    - faire des recommandations

---

## 🧼 Nettoyage et normalisation des données

> Avant l’insertion dans MongoDB, un travail de nettoyage approfondi a été réalisé :

### 1. Suppression des doublons
Stations et morceaux dédupliqués via leurs identifiants sources (`stationId`, `trackId`, `artistId`).

### 2. Gestion des valeurs nulles et des sentinelles
- `frequency` et `format` (stations) : respectivement 907 et 1099 valeurs manquantes sur 3 772 lignes à l'origine.
- **`trackId`/`artistId` = `-1`** dans `station-plays` lorsque la source n'a pas identifié le morceau/l'artiste (~328 lignes sur 10 000, 3,3%) → **exclues** des collections `tracks`, `artists` et `plays`.
- Champs premium (`cume`, URLs de streaming) marqués `"[PREMIUM]"` → normalisés en `null` (restriction commerciale de la source, pas une vraie absence de donnée).

### 3. ⚠️ Anomalie corrigée sur une première tentative de nettoyage
Une première version automatique avait comblé les valeurs manquantes de façon incorrecte :
- `format` manquant → rempli par `"Prov_" + fournisseur` (ex. `Prov_NPR`) — pas un vrai format radio. **173 lignes neutralisées en `null`.**
- `social_facebook` / `primary_pronouncement` remplis par la valeur la plus fréquente du dataset (`"BlackInformationNetwork"` sur 2008/3772 lignes) — champs hors périmètre du schéma final, sans impact.

### 4. Renommage des colonnes
Passage en `snake_case` cohérent (`station_id`, `call_letters`, `market_id`...).

### 5. Conversion des types et des identifiants
- `_id` de chaque collection = identifiant source original (`stationId`, `trackId`, `artistId`, `marketId`) réutilisé tel quel, pour un référencement direct entre collections sans remapping.
- `timestamp` (`plays`) : stocké en chaîne (`"2026-04-20 23:59:59"`), converti à la volée via `$toDate` dans les requêtes d'agrégation temporelles.


Cette étape est essentielle pour éviter les incohérences dans MongoDB, notamment lors des tris, filtres et agrégations.

---

# 🏛️ Choix des collections MongoDB

Le modèle NoSQL repose sur **5 collections principales**, choisies pour représenter les entités métier essentielles :
Base : `iheart_db` — 5 collections.

### **1. stations**
> La collection centrale du projet.  
> Elle regroupe l’identité de la station, son marché, ses genres, ses flux audio et ses réseaux sociaux.

### **2. tracks**
> Représente les morceaux diffusés sur les stations.

### **3. artists**
> Représente les artistes associés aux morceaux.

### **4. plays**
> Représente les événements de diffusion : quel morceau a été joué, sur quelle station, à quel moment.

### **5. markets**
> Représente les marchés radio (ville, état, pays).

Ce choix permet une modélisation claire, flexible et adaptée aux requêtes métier.


| Collection | Volume importé | Rôle |
|---|---|---|
| `markets` | 268 | Marché radio (ville, état, pays) |
| `stations` | 3 772 | Identité station, marché, format/genre, flux |
| `tracks` | 4 482 | Morceau diffusé (titre, album, durée, artistes) |
| `artists` | 2 414 | Artiste associé aux morceaux |
| `plays` | 9 672 | Événement de diffusion (station, morceau, horodatage) |


---

## 🧩 Diagramme Entité–Relation (ERD)


<img width="654" height="365" alt="Capture d’écran 2026-07-03 à 19 47 23" src="https://github.com/user-attachments/assets/5a75a1bd-9fe9-49a8-8f16-afab1dbc7f4c" />




- `markets` 1—N `stations` (référence `market_id`)
- `stations` 1—N `plays` (référence `station_id`)
- `tracks` 1—N `plays` (référence `track_id`)
- `artists` N—N `tracks` (via le tableau `artist_ids`)

**Choix de modélisation : référencement plutôt qu'imbrication** pour `plays` — vu le volume potentiel du dataset complet (246M+ lignes), imbriquer les plays dans les stations ferait exploser la taille des documents (limite MongoDB : 16 Mo/document). Chaque `play` reste un document léger, référencé.

### **Synthèse du modèle**
    - Un marché contient plusieurs stations.  
    - Une station génère plusieurs plays.  
    - Un morceau peut être joué plusieurs fois.  
    - Un artiste peut être associé à plusieurs morceaux.  
    - Les genres sont intégrés directement dans les stations.

Ce modèle est optimisé pour MongoDB : il évite les jointures complexes et permet des requêtes rapides.


### Exemple de document par collection

```json
// markets
{ "_id": 575, "city": "Los Angeles", "state": "CA", "country": "US" }

// stations
{
  "_id": 11386, "call_letters": "ASICS-FL", "name": "ASICS Radio",
  "frequency": null, "band": "FL", "format": null, "genre": "Sales Channels",
  "market_id": 575, "provider": "Clear Channel Digital", "stream_url": null
}

// artists
{ "_id": 31333415, "name": "Bad Bunny & Daddy Yankee" }

// tracks
{ "_id": 94093615, "title": "La Santa", "album": "YHLQMDLG", "duration": 206, "artist_ids": [31333415] }

// plays
{ "_id": "11141_1776729599", "station_id": 11141, "track_id": 94093615, "timestamp": "2026-04-20 23:59:59" }
```

---

## 🔎 Besoins utilisateurs & requêtes MongoDB (12 requêtes finales)

| # | Besoin | Collection principale |
|---|---|---|
| 1 | Identifier les radios ayant un format/genre particulier | `stations` |
| 2 | Voir les morceaux les plus joués sur une station | `stations` → `plays` → `tracks` |
| 3 | Analyser les genres dominants dans un état | `stations` → `markets` |
| 4 | Trouver les artistes les plus diffusés dans un marché (ville) | `plays` → `stations` → `markets` → `tracks` → `artists` |
| 5 | Voir les artistes associés à un morceau | `tracks` → `artists` |
| 6 | Identifier les stations avec le plus de plays | `plays` → `stations` |
| 7 | Quel état a le plus de stations actives | `stations` → `markets` |
| 8 | Marchés sans aucune station d'un genre donné | `markets` → `stations` |
| 9 | Diversité de programmation par station | `plays` → `stations` |
| 10 | Artistes avec la plus forte audience globale | `plays` → `tracks` → `artists` |
| 11 | Format générant le plus de diffusions à l'échelle nationale | `plays` → `stations` |
| 12 | Morceaux les plus longs / les plus courts | `tracks` |

**Note méthodologique :** les besoins portant initialement sur `cume` (audience déclarée par format/station) ont été reformulés autour du **volume de plays réellement mesuré**, car le champ `cume` est intégralement redacté (`[PREMIUM]`) dans l'échantillon gratuit du dataset.

Le détail complet des pipelines d'agrégation MongoDB est dans `requetes_mongodb.md`.

---

## 🔌 API Flask

Fichier : `app.py`. Expose les 12 requêtes sous forme d'endpoints REST paramétrables.

| # | Endpoint | Paramètres |
|---|---|---|
| 1 | `GET /api/stations/by-genre` | `?genre=Country` |
| 2 | `GET /api/stations/<name>/top-tracks` | `?limit=10` |
| 3 | `GET /api/genres/by-state` | `?state=CA` |
| 4 | `GET /api/artists/by-city` | `?city=Los Angeles&limit=10` |
| 5 | `GET /api/tracks/<title>/artists` | — |
| 6 | `GET /api/stations/top-plays` | `?limit=10` |
| 7 | `GET /api/states/top-station-count` | — |
| 8 | `GET /api/markets/without-genre` | `?genre=Classic Rock` |
| 9 | `GET /api/stations/diversity` | `?order=desc\|asc&limit=10` |
| 10 | `GET /api/artists/top-played` | `?limit=10` |
| 11 | `GET /api/formats/top-plays` | — |
| 12 | `GET /api/tracks/duration-extremes` | `?limit=5` |

Plus `GET /api/health` pour vérifier la connexion à MongoDB.

### Lancer l'API

```bash
pip install flask pymongo flask-cors
python app.py
```
→ disponible sur `http://127.0.0.1:5000`

---

## 🖥️ Interface Streamlit

Fichier : `streamlit_app.py`. Menu latéral avec les 12 analyses, formulaires de saisie (genre, état, ville, titre...), tableaux et graphiques (`bar_chart`).

### Lancer l'interface

```bash
pip install streamlit requests pandas
streamlit run streamlit_app.py
```
→ ouverture automatique sur `http://localhost:8501`

**Prérequis :** l'API Flask (`app.py`) doit tourner en parallèle (dans un terminal séparé) pour que Streamlit puisse l'interroger.

---

## 🚀 Démarrage complet du projet

```bash
# 1. Importer les données dans MongoDB
mongoimport --db iheart_db --collection markets  --file markets.json  --jsonArray
mongoimport --db iheart_db --collection stations --file stations.json --jsonArray
mongoimport --db iheart_db --collection artists  --file artists.json  --jsonArray
mongoimport --db iheart_db --collection tracks   --file tracks.json   --jsonArray
mongoimport --db iheart_db --collection plays    --file plays.json    --jsonArray

# 2. Lancer l'API (terminal 1)
python app.py

# 3. Lancer l'interface (terminal 2)
streamlit run streamlit_app.py
```

---

## 📂 Structure du projet

```
NO_SQL/
├── markets.json
├── stations.json
├── artists.json
├── tracks.json
├── plays.json
├── requetes_mongodb.md      # détail des 12 pipelines d'agrégation
├── app.py                   # API Flask
├── streamlit_app.py         # interface web
└── README.md                # ce fichier
```

---

## ✅ État d'avancement

- [x] Modélisation NoSQL (5 collections, ERD, choix référencement)
- [x] Nettoyage des données (doublons, valeurs manquantes, sentinelles)
- [x] Import MongoDB fonctionnel
- [x] 12 requêtes d'agrégation testées et validées dans `mongosh`
- [x] API Flask exposant les 12 requêtes
- [x] Interface Streamlit connectée à l'API
- [ ] Import du dataset complet (au-delà de l'échantillon d'1 jour)
- [ ] Conversion `timestamp` en `ISODate` natif à l'import
- [ ] Création des index de performance


