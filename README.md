# projetDevMLOps

Application en anglais car l'API de recettes que nous utilisons est en anglais.

# Description

Cette application permet de rechercher des recettes par ingrédients, nom de plat générique (exemples : pasta, cupcake, tiramisu) et nutriments, elle propose aussi des suggestions en fonction des recettes déjà likées par les différentes personnes utilisant l'application.


# Fonctionalités

Back-end :
- recherche de recette
- visualisation d'une recette
- like d'une recette
- voir les recommandations de l'IA

Front-end : 
- facilité d'utilisation, intuitif


# Lancer le projet en local : 

- Créer un .env à la racine du projet en copiant .env.example


## Mise en place de Garage

1. Démarrer le service Garage avec Docker Compose :
```shell
docker compose up garage -d
```

2. Vérifier que le service fonctionne :
```shell
docker exec -it garage /garage status
```

Mémoriser l'ID du node retourné.

3. Assigner un layout :
```shell
docker exec -it garage /garage layout assign -z dc1 -c 1G <node_id>
docker exec -it garage /garage layout apply --version 1
```

4. Créer un bucket de stockage puis vérifier sa création :
```shell
docker exec -it garage /garage bucket create mlflow-bucket
docker exec -it garage /garage bucket info mlflow-bucket
```

5. Créer une key pour le bucket puis l'assigner au bucket en lui donnant les permissions nécessaires :
```shell
docker exec -it garage /garage key create mlflow-key
docker exec -it garage /garage bucket allow --read --write --owner mlflow-bucket --key mlflow-key
```

Mémoriser la valeur de la key retournée (Key ID et Secret key).

6. Dans le fichier `docker-compose.yaml`, modifier les variables d'environnement `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY` pour le service `mlflow` avec les valeurs de la key mémorisées précédemment.

## Démarrer le service MLFlow avec Docker Compose et les autres conteneurs du projet :

Après avoir réaliser les étapes de mise en place de Garage, démarrer le service MLFlow :
```shell
docker compose up --build
```
Le modèle est entrainé au lancement de l'api

- pour avoir accès au différentes fonctions du back-end : http://localhost:8000/docs
- pour avoir accès au site (front et back) : http://localhost:5173/templates/index.html
- accès bdd : http://localhost:8080/ (sélectionner System : PostgreSQl ; server : db ; Username : user ; Password : password ; Database : food_bd)


# Utiliser MLFlow :

L'interface MLFlow est accessible à l'adresse : [http://localhost:5000](http://localhost:5000).

Pour utiliser MLFlow avec Python, installer la bibliothèque :
```shell
pip install mlflow
```

# Clef API Spoonacular

Nous avons utilisé des cléfs gratuites avec un accès limité journalier (nombre de requêtes limitées par jour)
Voici les différentes clef que nous avons générées : 
- c86fe6290a32478dad234905a465967d
- 0021762ed6ec47e8a69feb6d7d83aea1
- d151f6b398864fcca6acf14e7e62dff7
- fe515d7082da4a2eb7a7ee44917efc93
- 16a22d4845ef4c8e84d5980eeb61769c


# Lien GitHub Pages : 

https://marionm64.github.io/projetDevMLOps/


# Grafana

http://localhost:3000 | identifiant et mot de passe =  admin/admin


# Prometheus

http://localhost:9090



# Utilisation Grafana

- Pour connecter grafana et prometheus, sur grafana : 
connections -> data sources -> add new data source -> sélectionner prometheus -> mettre l'url : http//≤ip_ordi>:9090 -> save

- Pour observer les metrics sur grafana :
connection-> Data sources -> build a dashboard -> add visualization -> prometheus -> select metrics -> run queries -> save bashboard




