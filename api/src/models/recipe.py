from fastapi import FastAPI, HTTPException
import psycopg2
import os
import time

# Permet de se connecter à la BDD
def connect_db():

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    return conn

# initialise la bdd
def init_db():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER NOT NULL PRIMARY KEY,
            title VARCHAR(200),
            "like" INTEGER NOT NULL)""")        
        conn.commit()
        cur.close()
        conn.close()
        print("Base de données initialisée avec succès")
        return True
    except psycopg2.OperationalError as e:
        print("Erreur de connexion à la base de données:", e)


# récupèrer une recette de la bdd en fonction de son Id
def get_recipe(id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM recipe WHERE id=%s', (id,))
        rows = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return rows
    except psycopg2.OperationalError as e:
        print("Erreur de connexion à la base de données:", e)


# ajouter un recette dans la BDD
def add_recipe(recipe):
    id = recipe["id"]
    title = recipe["title"]
    rows = get_recipe(recipe["id"])
    if len(rows)==0 :
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO recipe(id, title, "like") VALUES(%s, %s, 0)', (id, title))
            conn.commit()
            cur.close()
            conn.close()
            print("recette ajoutée")
            return True
        except psycopg2.OperationalError as e:
            print("Erreur de connexion à la base de données:", e)
    else :
        print("déjà ajoutée")
        return True
    
# ajouter un like à une recette
def add_like_recipe(id_recipe):
    recipe = get_recipe(id_recipe)
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('UPDATE recipe SET "like" = (%s) WHERE id = (%s)', (recipe[0][2]+1, id_recipe))
        conn.commit()
        cur.close()
        conn.close()
        return recipe[0][2]+1
    except psycopg2.OperationalError as e:
            print("Erreur de connexion à la base de données:", e)

# récupérer toutes les recettes présentent en BDD
def get_recipes():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM recipe')
        rows = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return rows
    except psycopg2.OperationalError as e:
        print("Erreur de connexion à la base de données:", e)

# récupère le nombre de likes donnés pour une recette donnée
def get_like_by_recipe(id):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM recipe WHERE id=%s', (id,))
        rows = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        if len(rows)==0:
            return 0
        else :
            return rows[0][2]
    except psycopg2.OperationalError as e:
        print("Erreur de connexion à la base de données:", e)
