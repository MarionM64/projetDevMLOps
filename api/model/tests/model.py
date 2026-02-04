import os
import tempfile
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

class RecommendationModel(mlflow.pyfunc.PythonModel):

    def load_context(self, context):
        with open(context.artifacts["tfidf"], "rb") as f:
            self.tfidf = pickle.load(f)

        with open(context.artifacts["tfidf_matrix"], "rb") as f:
            self.tfidf_matrix = pickle.load(f)


    # FONCTION DE RECOMMANDATION basé sur recommend_implicit
    def predict(self, context, df_recettes):

        """
        Recommande des recettes basées sur le contenu des recettes likées.
        """
        # on charge les données
        N=5
        nb_a_selectionner = min(5, len(df_recettes)) 

        
        # Récupérer les index des recettes que l'utilisateur a aimées
        # On filtre le DataFrame pour ne garder que les likes
        liked_recipes_df = df_recettes[df_recettes["like"] > 0]  

        if liked_recipes_df.empty:
            nb_a_selectionner = min(N, len(df_recettes))
            return df_recettes.sample(n=nb_a_selectionner)[['id', 'nom']].apply(
                lambda row: (row['id'], row['nom'], 0), axis=1
            ).tolist()
        
        # On transforme les noms des recettes likées en vecteurs
        user_vectors = self.tfidf.transform(liked_recipes_df['nom'])
        
        # On fait la MOYENNE des vecteurs (Le goût moyen de l'utilisateur)
        user_profile = np.mean(user_vectors, axis=0)
        
        # Pour que Scikit-learn accepte le format, on s'assure que c'est bien un array 2D
        user_profile = np.asarray(user_profile)

        # 3. Calculer la similarité avec TOUTES les recettes
        # Cosine Similarity : 1 = Identique, 0 = Rien à voir
        cosine_sim = cosine_similarity(user_profile, self.tfidf_matrix)
        
        # cosine_sim est une liste de scores [[0.1, 0.9, 0.05...]]
        # On l'aplatit pour avoir une liste simple
        scores = cosine_sim.flatten()
        
        # 4. Trier les résultats
        # argsort donne les indices triés du plus petit au plus grand, on inverse avec [::-1]
        sorted_indices = scores.argsort()[::-1]

        # S'assurer que les indices ne dépassent pas la taille du DataFrame
        sorted_indices = [i for i in sorted_indices if i < len(df_recettes)]

        
        recommendations = []
        liked_ids = liked_recipes_df['id'].tolist()
        for idx in sorted_indices:
            recette_id = int(df_recettes.iloc[idx]['id'])
            recette_nom = str(df_recettes.iloc[idx]['nom'])
            score = float(scores[idx])
            
            # On ne recommande pas ce qu'il a déjà liké
            if recette_id not in liked_ids:
                recommendations.append((recette_id, recette_nom, round(score, 2)))
                
            if len(recommendations) >= 5:
                break
                
        return recommendations

def entrainement_modele():

    mlflow.set_tracking_uri("http://mlflow:5000")

    mlflow.set_experiment("Recommendation_model")

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

        mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=RecommendationModel(),
            artifacts={
                "tfidf": "tfidf.pkl",
                "tfidf_matrix": "tfidf_matrix.pkl"
            },
            registered_model_name="Recommendation_model"
        )

    client = mlflow.MlflowClient()
    versions = client.get_latest_versions(
        "Recommendation_model", stages=["None"]
    )

    if versions:
        client.transition_model_version_stage(
            name="Recommendation_model",
            version=versions[0].version,
            stage="Production"
        )
        print("✅ Modèle mis en Production")


    return tfidf, tfidf_matrix