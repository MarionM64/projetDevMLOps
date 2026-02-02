import os
import pandas as pd
from src.models.recipe import get_recipes
import numpy as np
import scipy.sparse as sparse
import pickle
import mlflow
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Préparation des données


def charger_bdd():
    """"
    charge les recettes depuis la base de données et les met dans un DataFrame pandas
    """
    recettes = get_recipes()
    df_recettes = pd.DataFrame(recettes, columns=['id', 'nom', 'like'])
    return df_recettes


def charger_likes_utilisateur():
    """l'utilisateur aime aléatoirement 5 des recettes dans la base de données
    """
    df_recettes = charger_bdd()
    nb_a_selectionner = min(5, len(df_recettes)) 
    likes_utilisateur = df_recettes['id'].sample(n=nb_a_selectionner).tolist()
    return likes_utilisateur

def entrainement_modele():

    mlflow.set_experiment("Recommendation_model")
    #charger les données
    df_recettes = charger_bdd()
    likes_utilisateur = charger_likes_utilisateur()


    with mlflow.start_run():
        # Paramètres NLP
        min_df = 1
        ngram_range = (1, 2) # On prend les mots seuls et les paires ("Gâteau", "Gâteau Chocolat")
        
        mlflow.log_params({"min_df": min_df, "ngram_range": str(ngram_range)})

        print("Vectorisation des recettes...")
        # TF-IDF va transformer les noms en vecteurs mathématiques
        tfidf = TfidfVectorizer(min_df=min_df, ngram_range=ngram_range)
        # On crée la "Matrice des Recettes"
        tfidf_matrix = tfidf.fit_transform(df_recettes['nom'])
        
        # Sauvegarde du Vectorizer (C'est ça le "modèle" maintenant)
        with open('tfidf.pkl', 'wb') as f:
            pickle.dump(tfidf, f)
            
        # On sauvegarde aussi la matrice des recettes (pour ne pas la recalculer à chaque requête)
        with open('tfidf_matrix.pkl', 'wb') as f:
            pickle.dump(tfidf_matrix, f)
            
        mlflow.log_artifact('tfidf.pkl')
        mlflow.log_artifact('tfidf_matrix.pkl')
        print("Modèle Content-Based sauvegardé.")

        #metriques mlflow
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
                
        # MÈTRIQUE 1 : Confiance Moyenne
        # (Est-ce que le modèle trouve des trucs très ressemblants ?)
        avg_similarity = np.mean(top_scores) if top_scores else 0
        
        # MÉTRIQUE 2 : Confiance Max
        # (Quel est le score de la meilleure recommandation ?)
        max_similarity = top_scores[0] if top_scores else 0

        print(f"Métriques calculées -> Moyenne: {avg_similarity:.4f}, Max: {max_similarity:.4f}")

        # 4. LOGGING DANS MLFLOW
        mlflow.log_metric("avg_similarity_score", avg_similarity)
        mlflow.log_metric("max_similarity_score", max_similarity)
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
