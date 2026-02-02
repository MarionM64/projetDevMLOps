# projetDevMLOPS

Application en anglais car l'API de recettes que nous utilisons est en anglais.

# Description

Cette aplication permet de rechercher des recettes par engrédients, nom de plat générique (exemples : pasta, cupcake, tiramisu) et nutriments, elle propose aussi des sugestions en fonction des recettes déjà likées par les différentes personnes utilisant l'application.


# Fonctionalitées

BACK :
- recherche de recette
- visualisation d'une recette
- like d'une recette
- voir les recommandations de l'IA

FRONT : 
- facilité d'utilisation, intuitif


# Lancer le projet en local : 

- créer un .env à la racine du projet en copiant collant .env.example
- docker compose up -d --build ou docker-compose up -d --build

- pour avoir accès au différentes fonctions du back : http://localhost:8000/docs
- pour avoir accès au site (front et back) : http://localhost:5173/templates/index.html
- accès bdd : http://localhost:8080/ (sélectioner System : PostgreSQl ; server : db ; Username : user ; Password : password ; Database : food_bd)


# Clef API Spoonacular

Nous avons utilisé des clef gratuite avec un accès limité journalier (nombres de requettes limitées par jour)
Voici les différentes clef que nous avons généré : 
- c86fe6290a32478dad234905a465967d
- 0021762ed6ec47e8a69feb6d7d83aea1
- d151f6b398864fcca6acf14e7e62dff7


# Lien GitHub Pages : 

https://marionm64.github.io/projetDevMLOps/


# Grafana

http://localhost:3000 | identifiant et mot de passe =  admin/admin


# Prometheus

http://localhost:9090



# Utilisation Grafana

- Pour connecter grafana et prometheus, sur grafana : 
connections -> data sources -> add new data source -> sélectionner prometheus -> mettre l'url : http//ip_ordi:9090 -> save

- Pour observer les metrics sur grafana :
connection-> Data sources -> build a bashboard -> add visualization -> prometheus -> select metrics -> run queries -> save bashboard


# MLFlow


