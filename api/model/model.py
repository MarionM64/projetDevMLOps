import pandas as pd
from api.src.models.recipe import get_recipes
import numpy as np
import scipy.sparse as sparse
import pickle
import mlflow
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Préparation des données
# Tables de toutes les recettes
recettes = get_recipes()



df_recettes = pd.DataFrame(recettes, columns=['id', 'nom', 'like'])

#utilisateur unique 
likes_utilisateur = [635574,715569]

#Entrainement du modèle
mlflow.set_experiment("Recommendation_model")

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

# --- 3. FONCTION DE RECOMMANDATION ---
def recommend_single_user(N=5):
    """
    Recommande des recettes basées sur le contenu des recettes likées.
    """
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
        recette_id = df_recettes.iloc[idx]['id']
        recette_nom = df_recettes.iloc[idx]['nom']
        score = scores[idx]
        
        # On ne recommande pas ce qu'il a déjà liké
        if recette_id not in likes_utilisateur:
            recommendations.append((recette_id, recette_nom, round(score, 2)))
            
        if len(recommendations) >= N:
            break
            
    return recommendations

# --- TEST ---
# On charge les modèles
with open('tfidf.pkl', 'rb') as f:
    tfidf = pickle.load(f)
with open('tfidf_matrix.pkl', 'rb') as f:
    tfidf_matrix = pickle.load(f)

print(f"L'utilisateur aime : {likes_utilisateur}")
recos = recommend_single_user()

print("Recommandations :")
for r in recos:
    print(f"- {r[1]} (Score: {r[2]})") 
    # Devrait recommander "Mousse au Chocolat" en premier car proche de "Gâteau Chocolat"