from fastapi import FastAPI, HTTPException
import psycopg2
import os
import time

def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS recipe (
            id INT PRIMARY KEY,
            like INT,
        )""")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Base de données initialisée avec succès")
        return True
    except psycopg2.OperationalError as e:
        print("Erreur de connexion à la base de données:", e)
