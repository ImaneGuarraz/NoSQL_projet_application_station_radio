# NoSQL_projet_application_station_radio

Application NoSQL de radio en ligne : une plateforme qui centralise des stations du monde entier, leurs flux audio, les morceaux diffusés et les artistes associés. Elle permet d’analyser les tendances, consulter l’historique, recommander des stations et exposer ces données via API et interface web dynamique.

---

## DATASET 

Ce dataset est adapté à un projet NoSQL car il contient des entités métier (stations, morceaux, artistes, diffusions) et un volume potentiellement important d’événements de diffusion. La structure documentaire de MongoDB permet de modéliser ces données de manière flexible, d’ajouter des métadonnées, et de répondre à des besoins d’analyse et de recommandation propres à une application de radio en ligne.

- Richesse des entités : le dataset contient au moins des stations, des morceaux (tracks), des artistes, et des événements de diffusion (plays).
- Données semi-structurées : certaines colonnes peuvent être enrichies (tags, genres multiples, métadonnées), ce qui se prête bien à des documents JSON.
- Volume et historique : les plays (diffusions) peuvent être très nombreux → NoSQL (MongoDB) est adapté pour stocker des logs d’événements.
- Flexibilité du schéma : il est possible d'ajouter des champs (popularité, tendances, recommandations) sans casser le schéma → typique d’un projet NoSQL.
- Cas d’usage réel : via ce dataset notre application de radio en ligne peut :
    - lister des stations
    - voir ce qui est diffusé
    - analyser les tendances
    - faire des recommandations


## CHOIX DES COLLECTIONS 

- 
- 
- 
- 
- 


Pour aller plus loin : 
- #### users
Elles stockent les préférences des auditeurs, leurs favoris et leurs habitudes, ce qui permet de personnaliser l’expérience et d’offrir des recommandations pertinentes.
