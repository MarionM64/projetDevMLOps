from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "db_food")
DB_NAME = os.getenv("POSTGRES_DB", "food_bd")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# Créer le moteur SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


# Définir le modèle Recette
class Recette(Base):
    __tablename__ = "recettes"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    temps_preparation = Column(Integer, nullable=True)
    nombre_portions = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)


# Créer les tables au démarrage
def init_db():
    """Crée toutes les tables en base de données"""
    Base.metadata.create_all(bind=engine)
    print("✓ Tables créées/vérifiées avec succès")


# Fonction pour obtenir une session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
