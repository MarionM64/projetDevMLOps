import os
import pandas as pd
import numpy as np
import scipy.sparse as sparse
import pickle
import mlflow
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Préparation des données


def charger_bdd():
    """"
    charge les recettes depuis la base de données et les met dans un DataFrame pandas
    """
    chemin_fichier = "model/tests/data.csv"
    
    # Charger le CSV dans un DataFrame
    df_recettes = pd.read_csv(chemin_fichier, usecols=['id', 'nom', 'like'])
    return df_recettes


def charger_likes_utilisateur():
    """l'utilisateur aime aléatoirement 5 des recettes dans la base de données
    """
    df_recettes = charger_bdd()
    nb_a_selectionner = min(5, len(df_recettes)) 
    likes_utilisateur = df_recettes['id'].sample(n=nb_a_selectionner).tolist()
    return likes_utilisateur



def entrainement_modele():
    print("0")
    mlflow.set_tracking_uri("http://localhost:5000")
    print("1")
    mlflow.set_experiment("Recommendation_model")
    print("2")
    #charger les données
    df_recettes = charger_bdd()
    likes_utilisateur = charger_likes_utilisateur()
    print("3")
    with mlflow.start_run(run_name="Content-Based Filtering"):
        #logger les parametres sur mlflow
        params = {
            "min_df": 1,
            "ngram_range": (1, 2),
            "analyzer": "word",
            "algorithm": "Cosine Similarity"
        }
        print("4")
        mlflow.log_params(params)
        
        print("Vectorisation des recettes...")
        # TF-IDF va transformer les noms en vecteurs mathématiques
        tfidf = TfidfVectorizer(min_df=params["min_df"], ngram_range=params["ngram_range"])

        # On crée la "Matrice des Recettes"
        tfidf_matrix = tfidf.fit_transform(df_recettes['nom'])

        #logger les metriques sur mlflow
        #calcul du profil utilisateur
        liked_df = df_recettes[df_recettes['id'].isin(likes_utilisateur)]
        user_vectors = tfidf.transform(liked_df['nom'])
        user_profile = np.mean(user_vectors, axis=0)
        user_profile = np.asarray(user_profile)

        # 2. On calcule les scores de similarité avec TOUT
        cosine_sim = cosine_similarity(user_profile, tfidf_matrix).flatten()
        
        # 3. On regarde les scores du Top 3 (hors recettes déjà likées)
        sorted_indices = cosine_sim.argsort()[::-1]
        
        top_scores = []
        for idx in sorted_indices:
            rid = df_recettes.iloc[idx]['id']
            if rid not in likes_utilisateur:
                top_scores.append(cosine_sim[idx])
            if len(top_scores) >= 3:
                break

        # On récupère les scores des items NON likés
        scores_candidats = [
                score for idx, score in enumerate(cosine_sim) 
                if df_recettes.iloc[idx]['id'] not in likes_utilisateur
            ]
        # Calcul des stats
        avg_sim = np.mean(scores_candidats) if scores_candidats else 0
        max_sim = np.max(scores_candidats) if scores_candidats else 0
            
        metrics = {
                "vocab_size": len(tfidf.vocabulary_),
                "avg_similarity_score": avg_sim,
                "max_similarity_score": max_sim,
                "nb_recettes_base": len(df_recettes)
        }   
        mlflow.log_metrics(metrics)

        
        #logger un Artefact Graphique : 
        # Histogramme des scores de similarité pour voir la distribution
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(cosine_sim, bins=20, color='#636EFA', alpha=0.7)
        ax.set_title("Distribution des scores de similarité (User Random)")
        ax.set_xlabel("Score Cosine")
        ax.set_ylabel("Nombre de recettes")
            
        plt.savefig("similarity_dist.png")
        mlflow.log_artifact("similarity_dist.png")
        plt.close()
        os.remove("similarity_dist.png")

        # Sauvegarder les modèles dans des fichiers
        with open('tfidf.pkl', 'wb') as f:
            pickle.dump(tfidf, f)
        with open('tfidf_matrix.pkl', 'wb') as f:
            pickle.dump(tfidf_matrix, f)
            
        mlflow.log_artifact('tfidf.pkl')
        mlflow.log_artifact('tfidf_matrix.pkl')

        mlflow.set_tags({
            "embedding": "TF-IDF",
            "status": "prod_candidate"
        })
    return tfidf, tfidf_matrix



def get_modeles():
    """
    Tente de charger les modèles. S'ils n'existent pas, lance l'entraînement.
    """
    # On vérifie si les deux fichiers existent
    if os.path.exists('tfidf.pkl') and os.path.exists('tfidf_matrix.pkl'):
        try:
            # Chargement des modèles depuis les fichiers
            with open('tfidf.pkl', 'rb') as f:
                tfidf = pickle.load(f)
            with open('tfidf_matrix.pkl', 'rb') as f:
                tfidf_matrix = pickle.load(f)
            return tfidf, tfidf_matrix
            
        except (EOFError, pickle.UnpicklingError):
            # Fichiers corrompus -> On relance l'entraînement
            return entrainement_modele()
    else:
        #Fichiers absents -> On lance l'entraînement
        return entrainement_modele()
    

# --- 3. FONCTION DE RECOMMANDATION ---
def recommend_implicit(N=5):
    """
    Recommande des recettes basées sur le contenu des recettes likées.
    """
    # Charger les données
    df_recettes = charger_bdd()
    likes_utilisateur = charger_likes_utilisateur()
    tfidf, tfidf_matrix = get_modeles()
    # Récupérer les index des recettes que l'utilisateur a aimées
    # On filtre le DataFrame pour ne garder que les likes
    liked_recipes_df = df_recettes[df_recettes['id'].isin(likes_utilisateur)]
    
    if liked_recipes_df.empty:
        return [] 
    
    # On transforme les noms des recettes likées en vecteurs
    user_vectors = tfidf.transform(liked_recipes_df['nom'])
    
    # On fait la MOYENNE des vecteurs (Le goût moyen de l'utilisateur)
    user_profile = np.mean(user_vectors, axis=0)
    
    # Pour que Scikit-learn accepte le format, on s'assure que c'est bien un array 2D
    user_profile = np.asarray(user_profile)

    # 3. Calculer la similarité avec TOUTES les recettes
    # Cosine Similarity : 1 = Identique, 0 = Rien à voir
    cosine_sim = cosine_similarity(user_profile, tfidf_matrix)
    
    # cosine_sim est une liste de scores [[0.1, 0.9, 0.05...]]
    # On l'aplatit pour avoir une liste simple
    scores = cosine_sim.flatten()
    
    # 4. Trier les résultats
    # argsort donne les indices triés du plus petit au plus grand, on inverse avec [::-1]
    sorted_indices = scores.argsort()[::-1]
    
    recommendations = []
    for idx in sorted_indices:
        recette_id = int(df_recettes.iloc[idx]['id'])
        recette_nom = str(df_recettes.iloc[idx]['nom'])
        score = float(scores[idx])
        
        # On ne recommande pas ce qu'il a déjà liké
        if recette_id not in likes_utilisateur:
            recommendations.append((recette_id, recette_nom, round(score, 2)))
            
        if len(recommendations) >= N:
            break
            
    return recommendations


get_modeles()
