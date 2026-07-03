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

Le dataset iHeartRadio contient :

    - des stations radio (identité, fréquence, format, audience, genres, flux audio)  
    - des marchés radio (ville, état, pays)  
    - des métadonnées (dates de modification, URLs, réseaux sociaux)  

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

### **1. Suppression des doublons**
Les stations dupliquées ont été identifiées et supprimées pour garantir l’unicité des documents.

### **2. Gestion des valeurs nulles**
Les valeurs manquantes ont été traitées selon leur importance :
- suppression des lignes très incomplètes
- imputation par médiane ou mode pour les colonnes numériques  
- remplacement des chaînes vides ou `"null"` par `NaN`

### **3. Renommage des colonnes**
Les colonnes ont été renommées pour obtenir une structure claire, cohérente et exploitable dans MongoDB.

### **4. Conversion des types**
Les types ont été normalisés :
- dates → `datetime`  
- nombres → `float` / `int`  
- booléens → `bool`  
- texte → `string`  
- genres → **listes Python** (au lieu de chaînes JSON)

Cette étape est essentielle pour éviter les incohérences dans MongoDB, notamment lors des tris, filtres et agrégations.

---

# 🏛️ Choix des collections MongoDB

Le modèle NoSQL repose sur **5 collections principales**, choisies pour représenter les entités métier essentielles :

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

---

# 🧩 Diagramme Entité–Relation (ERD)

Le modèle NoSQL repose sur les relations suivantes :
markets (market_id)
|
| 1 - N
v
stations (station_id, market_id, genres[], streaming, social)
|
| 1 - N
v
plays (play_id, station_id, track_id, play_timestamp)
^
| N - 1
|
tracks (track_id, title, duration, genre, artists[])
|
| N - N
v
artists (artist_id, name, country, genres[])


### **Synthèse du modèle**
    - Un marché contient plusieurs stations.  
    - Une station génère plusieurs plays.  
    - Un morceau peut être joué plusieurs fois.  
    - Un artiste peut être associé à plusieurs morceaux.  
    - Les genres sont intégrés directement dans les stations.

Ce modèle est optimisé pour MongoDB : il évite les jointures complexes et permet des requêtes rapides.

---

##  🎯 Besoins utilisateurs

Les besoins ont été définis en se plaçant du point de vue d’un analyste radio ou d’un responsable de programmation :

1. Identifier les stations les plus populaires dans un marché.  
2. Découvrir les stations par genre musical.  
3. Voir les morceaux les plus joués sur une station.  
4. Identifier les artistes les plus diffusés.  
5. Analyser les genres dominants dans une ville.  
6. Trouver les stations disposant d’un flux HLS.  
7. Visualiser les plays par jour pour une station.  
8. Identifier les stations avec le plus grand nombre de plays.  
9. Trouver les morceaux les plus longs.  
10. Voir les artistes associés à un track.  
11. Trouver les stations qui diffusent un artiste donné.  
12. Analyser les tendances musicales par marché.  
13. Voir les stations d’un pays spécifique.  
14. Identifier les stations avec talkback activé.  
15. Trouver les stations d’un format particulier.

> Ces besoins guident la création des requêtes MongoDB.

---


